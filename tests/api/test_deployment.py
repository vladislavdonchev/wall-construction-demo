"""Deployment tests for Wall Construction API.

Tests that verify the full stack is properly deployed and functional:
- Database migrations have run successfully
- API endpoints are accessible and return correct status codes
- CRUD operations work end-to-end
- Data persistence works correctly
"""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.profiles.models import Simulation


@pytest.mark.django_db
@pytest.mark.deployment
class TestDeploymentHealth:
    """Test deployment health and basic API functionality."""

    def test_api_root_accessible(self, api_client: APIClient) -> None:
        """Test API root endpoint is accessible."""
        url = "/"

        response = api_client.get(url)

        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_301_MOVED_PERMANENTLY,
            status.HTTP_302_FOUND,
        )

    def test_profiles_endpoint_accessible(self, api_client: APIClient) -> None:
        """Test profiles list endpoint returns 200 with empty database."""
        url = reverse("profile-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
        assert isinstance(response.data["results"], list)

    def test_wallsections_endpoint_accessible(self, api_client: APIClient) -> None:
        """Test wallsections list endpoint returns 200 with empty database."""
        url = reverse("wallsection-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data
        assert isinstance(response.data["results"], list)


@pytest.mark.django_db
@pytest.mark.deployment
class TestDeploymentEndToEnd:
    """Test end-to-end workflows to verify deployment integrity."""

    def test_create_profile_and_retrieve(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test creating a profile and retrieving it verifies database works."""
        list_url = reverse("profile-list")

        # Create profile
        create_payload = {
            "simulation": simulation.id,
            "name": "Deployment Test Profile",
            "team_lead": "Test Lead",
            "is_active": True,
        }
        create_response = api_client.post(list_url, create_payload, format="json")

        assert create_response.status_code == status.HTTP_201_CREATED
        assert create_response.data["name"] == "Deployment Test Profile"
        assert "id" in create_response.data

        profile_id = create_response.data["id"]

        # Retrieve profile
        detail_url = reverse("profile-detail", kwargs={"pk": profile_id})
        retrieve_response = api_client.get(detail_url)

        assert retrieve_response.status_code == status.HTTP_200_OK
        assert retrieve_response.data["id"] == profile_id
        assert retrieve_response.data["name"] == "Deployment Test Profile"
        assert retrieve_response.data["team_lead"] == "Test Lead"

    def test_create_wallsection_with_profile(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test creating wallsection with profile verifies foreign keys work."""
        # Create profile first
        profile_url = reverse("profile-list")
        profile_payload = {"simulation": simulation.id, "name": "Wall Builder", "team_lead": "Builder Lead"}
        profile_response = api_client.post(
            profile_url,
            profile_payload,
            format="json",
        )
        assert profile_response.status_code == status.HTTP_201_CREATED
        profile_id = profile_response.data["id"]

        # Create wallsection
        wallsection_url = reverse("wallsection-list")
        wallsection_payload = {
            "profile": profile_id,
            "section_name": "Section 1",
        }
        wallsection_response = api_client.post(
            wallsection_url,
            wallsection_payload,
            format="json",
        )

        assert wallsection_response.status_code == status.HTTP_201_CREATED
        assert wallsection_response.data["profile"] == profile_id
        assert wallsection_response.data["section_name"] == "Section 1"
        assert "id" in wallsection_response.data

    def test_list_profiles_after_creation(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test listing profiles returns created profiles."""
        url = reverse("profile-list")

        # Create multiple profiles
        for i in range(3):
            payload = {
                "simulation": simulation.id,
                "name": f"Profile {i}",
                "team_lead": f"Lead {i}",
            }
            create_response = api_client.post(url, payload, format="json")
            assert create_response.status_code == status.HTTP_201_CREATED

        # List all profiles
        list_response = api_client.get(url)

        assert list_response.status_code == status.HTTP_200_OK
        assert list_response.data["count"] == 3
        assert len(list_response.data["results"]) == 3

    def test_update_profile(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test updating a profile verifies write operations work."""
        # Create profile
        list_url = reverse("profile-list")
        create_payload = {"simulation": simulation.id, "name": "Original Name", "team_lead": "Original Lead"}
        create_response = api_client.post(list_url, create_payload, format="json")
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.data["id"]

        # Update profile
        detail_url = reverse("profile-detail", kwargs={"pk": profile_id})
        update_payload = {
            "simulation": simulation.id,
            "name": "Updated Name",
            "team_lead": "Updated Lead",
            "is_active": False,
        }
        update_response = api_client.put(detail_url, update_payload, format="json")

        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data["name"] == "Updated Name"
        assert update_response.data["team_lead"] == "Updated Lead"
        assert update_response.data["is_active"] is False

    def test_delete_profile(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test deleting a profile verifies delete operations work."""
        # Create profile
        list_url = reverse("profile-list")
        create_payload = {"simulation": simulation.id, "name": "To Delete", "team_lead": "Delete Lead"}
        create_response = api_client.post(list_url, create_payload, format="json")
        assert create_response.status_code == status.HTTP_201_CREATED
        profile_id = create_response.data["id"]

        # Delete profile
        detail_url = reverse("profile-detail", kwargs={"pk": profile_id})
        delete_response = api_client.delete(detail_url)

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        retrieve_response = api_client.get(detail_url)
        assert retrieve_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.deployment
class TestDatabaseMigrations:
    """Test that database migrations have been applied correctly."""

    def test_profile_model_exists(self, api_client: APIClient) -> None:
        """Test Profile model table exists and is accessible."""
        url = reverse("profile-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_wallsection_model_exists(self, api_client: APIClient) -> None:
        """Test WallSection model table exists and is accessible."""
        url = reverse("wallsection-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_profile_fields_exist(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test Profile model has all required fields."""
        url = reverse("profile-list")
        payload = {
            "simulation": simulation.id,
            "name": "Field Test",
            "team_lead": "Test Lead",
            "is_active": True,
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert "name" in response.data
        assert "team_lead" in response.data
        assert "is_active" in response.data
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_wallsection_fields_exist(self, api_client: APIClient, simulation: Simulation) -> None:
        """Test WallSection model has all required fields."""
        # Create profile first
        profile_url = reverse("profile-list")
        profile_response = api_client.post(
            profile_url,
            {"simulation": simulation.id, "name": "Test", "team_lead": "Lead"},
            format="json",
        )
        profile_id = profile_response.data["id"]

        # Create wallsection
        url = reverse("wallsection-list")
        payload = {
            "profile": profile_id,
            "section_name": "Test Section",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert "profile" in response.data
        assert "section_name" in response.data
        assert "created_at" in response.data
