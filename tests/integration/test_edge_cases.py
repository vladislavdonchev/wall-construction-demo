"""Integration tests for edge cases and error paths."""

from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.integration
class TestEdgeCases:
    """Test edge cases and error handling paths."""

    def test_simulate_with_invalid_start_date_format(self, api_client: APIClient) -> None:
        """Test /simulate/ rejects invalid start_date format."""
        response = api_client.post(
            "/api/profiles/simulate/",
            {"config": "5", "num_teams": 10, "start_date": "invalid-date"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "start_date" in response.data
        assert "YYYY-MM-DD format" in str(response.data["start_date"])

    def test_overview_by_day_with_no_simulation_data(self, api_client: APIClient) -> None:
        """Test profile-specific /overview/<day>/ returns 404 when profile has no simulation data."""
        # Create a profile but run no simulation
        profile_response = api_client.post(
            "/api/profiles/",
            {"name": "Test Profile", "team_lead": "Test Lead"},
            format="json",
        )
        profile_id = profile_response.data["id"]

        # Request overview for day 1
        response = api_client.get(f"/api/profiles/{profile_id}/overview/1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "detail" in response.data
        assert "No simulation data for this profile" in response.data["detail"]
