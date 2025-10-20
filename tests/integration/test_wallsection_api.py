"""Integration tests for WallSection API endpoints."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
@pytest.mark.integration
class TestWallSectionAPI:
    """Test WallSection CRUD operations via REST API."""

    def test_create_wall_section_success(self, api_client: APIClient) -> None:
        """Test creating a wall section for a profile returns 201."""
        profile_url = reverse("profile-list")
        profile = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data

        url = reverse("wallsection-list")
        payload = {
            "profile": profile["id"],
            "section_name": "Tower 1-2",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["section_name"] == "Tower 1-2"
        assert response.data["profile"] == profile["id"]
        assert "id" in response.data
        assert "created_at" in response.data

    def test_create_wall_section_duplicate_name_for_profile_fails(self, api_client: APIClient) -> None:
        """Test duplicate section name for same profile returns 400."""
        profile_url = reverse("profile-list")
        profile = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data

        url = reverse("wallsection-list")
        payload = {
            "profile": profile["id"],
            "section_name": "Tower 1-2",
        }

        api_client.post(url, payload, format="json")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_wall_section_same_name_different_profiles_succeeds(self, api_client: APIClient) -> None:
        """Test same section name for different profiles is allowed."""
        profile_url = reverse("profile-list")
        profile1 = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data
        profile2 = api_client.post(
            profile_url,
            {"name": "Eastern Defense", "team_lead": "Tormund"},
            format="json",
        ).data

        url = reverse("wallsection-list")
        payload1 = {
            "profile": profile1["id"],
            "section_name": "Tower 1-2",
        }
        payload2 = {
            "profile": profile2["id"],
            "section_name": "Tower 1-2",
        }

        response1 = api_client.post(url, payload1, format="json")
        response2 = api_client.post(url, payload2, format="json")

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED

    def test_list_wall_sections(self, api_client: APIClient) -> None:
        """Test listing wall sections returns all sections."""
        profile_url = reverse("profile-list")
        profile = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data

        section_url = reverse("wallsection-list")
        api_client.post(
            section_url,
            {
                "profile": profile["id"],
                "section_name": "Tower 1-2",
            },
            format="json",
        )
        api_client.post(
            section_url,
            {
                "profile": profile["id"],
                "section_name": "Tower 2-3",
            },
            format="json",
        )

        response = api_client.get(section_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

    def test_filter_wall_sections_by_profile(self, api_client: APIClient) -> None:
        """Test filtering sections by profile ID."""
        profile_url = reverse("profile-list")
        profile1 = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data
        profile2 = api_client.post(
            profile_url,
            {"name": "Eastern Defense", "team_lead": "Tormund"},
            format="json",
        ).data

        section_url = reverse("wallsection-list")
        api_client.post(
            section_url,
            {
                "profile": profile1["id"],
                "section_name": "Tower 1-2",
            },
            format="json",
        )
        api_client.post(
            section_url,
            {
                "profile": profile2["id"],
                "section_name": "Tower 3-4",
            },
            format="json",
        )

        response = api_client.get(section_url, {"profile": profile1["id"]})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["section_name"] == "Tower 1-2"

    def test_retrieve_wall_section(self, api_client: APIClient) -> None:
        """Test retrieving a specific wall section."""
        profile_url = reverse("profile-list")
        profile = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data

        section_url = reverse("wallsection-list")
        section = api_client.post(
            section_url,
            {
                "profile": profile["id"],
                "section_name": "Tower 1-2",
            },
            format="json",
        ).data

        detail_url = reverse("wallsection-detail", kwargs={"pk": section["id"]})
        response = api_client.get(detail_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == section["id"]
        assert response.data["section_name"] == "Tower 1-2"

    def test_update_wall_section(self, api_client: APIClient) -> None:
        """Test updating a wall section."""
        profile_url = reverse("profile-list")
        profile = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data

        section_url = reverse("wallsection-list")
        section = api_client.post(
            section_url,
            {
                "profile": profile["id"],
                "section_name": "Tower 1-2",
            },
            format="json",
        ).data

        detail_url = reverse("wallsection-detail", kwargs={"pk": section["id"]})
        updated_payload = {
            "profile": profile["id"],
            "section_name": "Tower 1-2 Extended",
        }
        response = api_client.put(detail_url, updated_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["section_name"] == "Tower 1-2 Extended"

    def test_delete_wall_section(self, api_client: APIClient) -> None:
        """Test deleting a wall section."""
        profile_url = reverse("profile-list")
        profile = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data

        section_url = reverse("wallsection-list")
        section = api_client.post(
            section_url,
            {
                "profile": profile["id"],
                "section_name": "Tower 1-2",
            },
            format="json",
        ).data

        detail_url = reverse("wallsection-detail", kwargs={"pk": section["id"]})
        response = api_client.delete(detail_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        retrieve_response = api_client.get(detail_url)
        assert retrieve_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_profile_cascades_to_sections(self, api_client: APIClient) -> None:
        """Test deleting a profile also deletes associated wall sections."""
        profile_url = reverse("profile-list")
        profile = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data

        section_url = reverse("wallsection-list")
        section = api_client.post(
            section_url,
            {
                "profile": profile["id"],
                "section_name": "Tower 1-2",
            },
            format="json",
        ).data

        profile_detail_url = reverse("profile-detail", kwargs={"pk": profile["id"]})
        api_client.delete(profile_detail_url)

        section_detail_url = reverse("wallsection-detail", kwargs={"pk": section["id"]})
        response = api_client.get(section_detail_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_wall_section_requires_profile(self, api_client: APIClient) -> None:
        """Test creating section without profile returns 400."""
        url = reverse("wallsection-list")
        payload = {
            "section_name": "Tower 1-2",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "profile" in response.data

    def test_wall_section_requires_section_name(self, api_client: APIClient) -> None:
        """Test creating section without section_name returns 400."""
        profile_url = reverse("profile-list")
        profile = api_client.post(
            profile_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        ).data

        url = reverse("wallsection-list")
        payload = {
            "profile": profile["id"],
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "section_name" in response.data
