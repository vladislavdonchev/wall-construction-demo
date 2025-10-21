"""Integration tests for simulation API endpoints."""

from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.profiles.models import DailyProgress, Profile, WallSection


@pytest.mark.django_db
class TestSimulationAPI:
    """Test cases for simulation API endpoints."""

    def test_simulate_endpoint_creates_profiles_and_sections(
        self,
        api_client: APIClient,
    ) -> None:
        """Test that simulation endpoint creates profiles and sections."""
        config_data = {
            "config": "21 25 28\n17\n17 22 17 19 17",
            "num_teams": 4,
            "start_date": "2025-10-20",
        }

        response = api_client.post("/api/profiles/simulate/", config_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Profile.objects.count() == 3
        assert WallSection.objects.count() == 9

    def test_simulate_endpoint_runs_simulation(
        self,
        api_client: APIClient,
    ) -> None:
        """Test that simulation endpoint creates daily progress records."""
        config_data = {
            "config": "28 29",
            "num_teams": 2,
            "start_date": "2025-10-20",
        }

        response = api_client.post("/api/profiles/simulate/", config_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DailyProgress.objects.count() > 0

        assert response.data["total_sections"] == 2
        assert int(response.data["total_days"]) > 0

    def test_simulate_endpoint_validates_config(
        self,
        api_client: APIClient,
    ) -> None:
        """Test that simulation endpoint validates config."""
        config_data = {
            "config": "21 abc 28",
            "num_teams": 2,
        }

        response = api_client.post("/api/profiles/simulate/", config_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "config" in response.data
        assert "Invalid number format" in str(response.data["config"])

    def test_simulate_endpoint_requires_config(
        self,
        api_client: APIClient,
    ) -> None:
        """Test that simulation endpoint requires config."""
        config_data = {
            "num_teams": 2,
        }

        response = api_client.post("/api/profiles/simulate/", config_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "config" in response.data
        assert "config parameter is required" in str(response.data["config"])

    def test_simulate_endpoint_validates_num_teams(
        self,
        api_client: APIClient,
    ) -> None:
        """Test that simulation endpoint validates num_teams."""
        config_data = {
            "config": "21 25 28",
            "num_teams": -1,
        }

        response = api_client.post("/api/profiles/simulate/", config_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "num_teams" in response.data
        assert "must be at least" in str(response.data["num_teams"])

    def test_days_endpoint_returns_ice_usage(
        self,
        api_client: APIClient,
    ) -> None:
        """Test GET /profiles/<id>/days/<day>/ endpoint."""
        config_data = {
            "config": "28 29",
            "num_teams": 2,
            "start_date": "2025-10-20",
        }

        api_client.post("/api/profiles/simulate/", config_data, format="json")

        profile = Profile.objects.first()
        assert profile is not None

        response = api_client.get(f"/api/profiles/{profile.id}/days/1/")

        assert response.status_code == status.HTTP_200_OK
        assert "day" in response.data
        assert "total_feet_built" in response.data
        assert "total_ice_cubic_yards" in response.data
        assert "sections" in response.data
        assert response.data["day"] == 1
        assert isinstance(response.data["sections"], list)
        assert len(response.data["sections"]) == 2

    def test_days_endpoint_returns_404_for_no_data(
        self,
        api_client: APIClient,
    ) -> None:
        """Test days endpoint returns 404 when no simulation data."""
        profile = Profile.objects.create(name="Test", team_lead="Lead")

        response = api_client.get(f"/api/profiles/{profile.id}/days/1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_overview_by_day_endpoint(
        self,
        api_client: APIClient,
    ) -> None:
        """Test GET /profiles/<id>/overview/<day>/ endpoint."""
        config_data = {
            "config": "28 29",
            "num_teams": 2,
            "start_date": "2025-10-20",
        }

        api_client.post("/api/profiles/simulate/", config_data, format="json")

        profile = Profile.objects.first()
        assert profile is not None

        response = api_client.get(f"/api/profiles/{profile.id}/overview/1/")

        assert response.status_code == status.HTTP_200_OK
        assert "day" in response.data
        assert "cost" in response.data
        assert response.data["day"] == "1"

    def test_overview_all_by_day_endpoint(
        self,
        api_client: APIClient,
    ) -> None:
        """Test GET /profiles/overview/<day>/ endpoint."""
        config_data = {
            "config": "28\n29",
            "num_teams": 2,
            "start_date": "2025-10-20",
        }

        api_client.post("/api/profiles/simulate/", config_data, format="json")

        response = api_client.get("/api/profiles/overview/1/")

        assert response.status_code == status.HTTP_200_OK
        assert "day" in response.data
        assert "cost" in response.data
        assert response.data["day"] == "1"

    def test_overview_total_endpoint(
        self,
        api_client: APIClient,
    ) -> None:
        """Test GET /profiles/overview/ endpoint returns total days.

        The endpoint now calculates and returns the actual number of
        construction days from DailyProgress records instead of None.
        """
        config_data = {
            "config": "28 29",
            "num_teams": 2,
            "start_date": "2025-10-20",
        }

        api_client.post("/api/profiles/simulate/", config_data, format="json")

        response = api_client.get("/api/profiles/overview/")

        assert response.status_code == status.HTTP_200_OK
        assert "day" in response.data
        assert "cost" in response.data
        # Verify day is now calculated from simulation data
        assert response.data["day"] > 0
        assert isinstance(response.data["day"], int)

    def test_spec_example_simulation(
        self,
        api_client: APIClient,
    ) -> None:
        """Test simulation with spec example data."""
        config_data = {
            "config": "21 25 28\n17\n17 22 17 19 17",
            "num_teams": 20,
            "start_date": "2025-10-20",
        }

        response = api_client.post("/api/profiles/simulate/", config_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["total_sections"] == 9

        profile_1 = Profile.objects.get(name="Profile 1")

        day_1_response = api_client.get(f"/api/profiles/{profile_1.id}/days/1/")
        assert day_1_response.status_code == status.HTTP_200_OK
        assert day_1_response.data["total_ice_cubic_yards"] == "585"

        overview_response = api_client.get("/api/profiles/overview/")
        assert overview_response.status_code == status.HTTP_200_OK
