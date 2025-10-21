"""Integration tests for Profile API endpoints."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.profiles.models import Simulation


@pytest.mark.django_db
@pytest.mark.integration
class TestProfileAPI:
    """Test Profile CRUD operations via REST API."""

    def test_create_profile_success(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test creating a new profile returns 201 and correct data."""
        url = reverse("profile-list")
        payload = {
            "simulation": simulation.id,
            "name": "Northern Watch",
            "team_lead": "Jon Snow",
            "is_active": True,
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Northern Watch"
        assert response.data["team_lead"] == "Jon Snow"
        assert response.data["is_active"] is True
        assert "id" in response.data
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_create_profile_duplicate_name_fails(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test creating profile with duplicate name returns 400."""
        url = reverse("profile-list")
        payload = {"simulation": simulation.id, "name": "Northern Watch", "team_lead": "Jon Snow"}

        api_client.post(url, payload, format="json")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_profiles_empty(self, api_client: APIClient) -> None:
        """Test listing profiles when none exist returns empty results."""
        url = reverse("profile-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_profiles_with_data(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test listing profiles returns all profiles ordered by created_at."""
        url = reverse("profile-list")
        api_client.post(
            url,
            {"simulation": simulation.id, "name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        )
        api_client.post(
            url,
            {"simulation": simulation.id, "name": "Eastern Defense", "team_lead": "Tormund Giantsbane"},
            format="json",
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["name"] == "Eastern Defense"
        assert response.data["results"][1]["name"] == "Northern Watch"

    def test_retrieve_profile_success(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test retrieving a profile by ID returns 200 and correct data."""
        create_url = reverse("profile-list")
        create_response = api_client.post(
            create_url,
            {"simulation": simulation.id, "name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        )
        profile_id = create_response.data["id"]

        retrieve_url = reverse("profile-detail", kwargs={"pk": profile_id})
        response = api_client.get(retrieve_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == profile_id
        assert response.data["name"] == "Northern Watch"
        assert response.data["team_lead"] == "Jon Snow"

    def test_retrieve_profile_not_found(self, api_client: APIClient) -> None:
        """Test retrieving non-existent profile returns 404."""
        url = reverse("profile-detail", kwargs={"pk": 99999})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_profile_success(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test updating a profile via PUT returns 200 and updated data."""
        create_url = reverse("profile-list")
        create_response = api_client.post(
            create_url,
            {"simulation": simulation.id, "name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        )
        profile_id = create_response.data["id"]

        update_url = reverse("profile-detail", kwargs={"pk": profile_id})
        updated_payload = {
            "simulation": simulation.id,
            "name": "Northern Watch Updated",
            "team_lead": "Samwell Tarly",
            "is_active": False,
        }
        response = api_client.put(update_url, updated_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Northern Watch Updated"
        assert response.data["team_lead"] == "Samwell Tarly"
        assert response.data["is_active"] is False

    def test_partial_update_profile_success(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test partially updating profile via PATCH returns 200."""
        create_url = reverse("profile-list")
        create_response = api_client.post(
            create_url,
            {"simulation": simulation.id, "name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        )
        profile_id = create_response.data["id"]

        update_url = reverse("profile-detail", kwargs={"pk": profile_id})
        response = api_client.patch(
            update_url,
            {"is_active": False},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_active"] is False
        assert response.data["name"] == "Northern Watch"
        assert response.data["team_lead"] == "Jon Snow"

    def test_delete_profile_success(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test deleting a profile returns 204."""
        create_url = reverse("profile-list")
        create_response = api_client.post(
            create_url,
            {"simulation": simulation.id, "name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        )
        profile_id = create_response.data["id"]

        delete_url = reverse("profile-detail", kwargs={"pk": profile_id})
        response = api_client.delete(delete_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        retrieve_response = api_client.get(delete_url)
        assert retrieve_response.status_code == status.HTTP_404_NOT_FOUND

    def test_profile_name_required(self, api_client: APIClient) -> None:
        """Test creating profile without name returns 400."""
        url = reverse("profile-list")
        payload = {"team_lead": "Jon Snow"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_profile_team_lead_required(self, api_client: APIClient) -> None:
        """Test creating profile without team_lead returns 400."""
        url = reverse("profile-list")
        payload = {"name": "Northern Watch"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "team_lead" in response.data

    def test_profile_defaults(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test profile creation with default values."""
        url = reverse("profile-list")
        payload = {"simulation": simulation.id, "name": "Northern Watch", "team_lead": "Jon Snow"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_active"] is True
