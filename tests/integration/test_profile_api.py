"""Integration tests for Profile API endpoints."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.profiles.models import DailyProgress, Profile, WallSection


@pytest.mark.django_db
@pytest.mark.integration
class TestProfileAPI:
    """Test Profile CRUD operations via REST API."""

    def test_create_profile_success(self, api_client: APIClient) -> None:
        """Test creating a new profile returns 201 and correct data."""
        url = reverse("profile-list")
        payload = {
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

    def test_create_profile_duplicate_name_fails(self, api_client: APIClient) -> None:
        """Test creating profile with duplicate name returns 400."""
        url = reverse("profile-list")
        payload = {"name": "Northern Watch", "team_lead": "Jon Snow"}

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

    def test_list_profiles_with_data(self, api_client: APIClient) -> None:
        """Test listing profiles returns all profiles ordered by created_at."""
        url = reverse("profile-list")
        api_client.post(
            url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        )
        api_client.post(
            url,
            {"name": "Eastern Defense", "team_lead": "Tormund Giantsbane"},
            format="json",
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["name"] == "Eastern Defense"
        assert response.data["results"][1]["name"] == "Northern Watch"

    def test_retrieve_profile_success(self, api_client: APIClient) -> None:
        """Test retrieving a profile by ID returns 200 and correct data."""
        create_url = reverse("profile-list")
        create_response = api_client.post(
            create_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
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

    def test_update_profile_success(self, api_client: APIClient) -> None:
        """Test updating a profile via PUT returns 200 and updated data."""
        create_url = reverse("profile-list")
        create_response = api_client.post(
            create_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
            format="json",
        )
        profile_id = create_response.data["id"]

        update_url = reverse("profile-detail", kwargs={"pk": profile_id})
        updated_payload = {
            "name": "Northern Watch Updated",
            "team_lead": "Samwell Tarly",
            "is_active": False,
        }
        response = api_client.put(update_url, updated_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Northern Watch Updated"
        assert response.data["team_lead"] == "Samwell Tarly"
        assert response.data["is_active"] is False

    def test_partial_update_profile_success(self, api_client: APIClient) -> None:
        """Test partially updating profile via PATCH returns 200."""
        create_url = reverse("profile-list")
        create_response = api_client.post(
            create_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
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

    def test_delete_profile_success(self, api_client: APIClient) -> None:
        """Test deleting a profile returns 204."""
        create_url = reverse("profile-list")
        create_response = api_client.post(
            create_url,
            {"name": "Northern Watch", "team_lead": "Jon Snow"},
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

    def test_profile_defaults(self, api_client: APIClient) -> None:
        """Test profile creation with default values."""
        url = reverse("profile-list")
        payload = {"name": "Northern Watch", "team_lead": "Jon Snow"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_active"] is True

    def test_daily_ice_usage_success(self, api_client: APIClient) -> None:
        """Test daily ice usage endpoint returns aggregated data."""
        # Create profile
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        # Create wall sections
        section1 = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )
        section2 = WallSection.objects.create(
            profile=profile,
            section_name="Tower 2-3",
            start_position=Decimal("500.00"),
            target_length_feet=Decimal("500.00"),
        )

        # Create daily progress for same date
        target_date = date(2025, 10, 15)
        DailyProgress.objects.create(
            wall_section=section1,
            date=target_date,
            feet_built=Decimal("12.50"),
            ice_cubic_yards=Decimal("2437.50"),
            cost_gold_dragons=Decimal("4631250.00"),
        )
        DailyProgress.objects.create(
            wall_section=section2,
            date=target_date,
            feet_built=Decimal("16.25"),
            ice_cubic_yards=Decimal("3168.75"),
            cost_gold_dragons=Decimal("6020625.00"),
        )

        url = reverse("profile-daily-ice-usage", kwargs={"pk": profile.id})
        response = api_client.get(url, {"date": "2025-10-15"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile_id"] == profile.id
        assert response.data["profile_name"] == "Northern Watch"
        assert response.data["date"] == "2025-10-15"
        assert response.data["total_feet_built"] == "28.75"
        assert response.data["total_ice_cubic_yards"] == "5606.25"
        assert len(response.data["sections"]) == 2

    def test_daily_ice_usage_no_data_for_date(self, api_client: APIClient) -> None:
        """Test daily ice usage when no progress exists for given date."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        url = reverse("profile-daily-ice-usage", kwargs={"pk": profile.id})
        response = api_client.get(url, {"date": "2025-10-15"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_feet_built"] == "0.00"
        assert response.data["total_ice_cubic_yards"] == "0.00"
        assert response.data["sections"] == []

    def test_daily_ice_usage_invalid_profile(self, api_client: APIClient) -> None:
        """Test daily ice usage with non-existent profile returns 404."""
        url = reverse("profile-daily-ice-usage", kwargs={"pk": 9999})
        response = api_client.get(url, {"date": "2025-10-15"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_daily_ice_usage_missing_date_param(self, api_client: APIClient) -> None:
        """Test daily ice usage without date parameter returns 400."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        url = reverse("profile-daily-ice-usage", kwargs={"pk": profile.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cost_overview_success(self, api_client: APIClient) -> None:
        """Test cost overview endpoint returns aggregated data for date range."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        DailyProgress.objects.create(
            wall_section=section,
            date=date(2025, 10, 1),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )
        DailyProgress.objects.create(
            wall_section=section,
            date=date(2025, 10, 2),
            feet_built=Decimal("15.00"),
            ice_cubic_yards=Decimal("2925.00"),
            cost_gold_dragons=Decimal("5557500.00"),
        )
        DailyProgress.objects.create(
            wall_section=section,
            date=date(2025, 10, 3),
            feet_built=Decimal("20.00"),
            ice_cubic_yards=Decimal("3900.00"),
            cost_gold_dragons=Decimal("7410000.00"),
        )

        url = reverse("profile-cost-overview", kwargs={"pk": profile.id})
        response = api_client.get(url, {"start_date": "2025-10-01", "end_date": "2025-10-03"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["profile_id"] == profile.id
        assert response.data["profile_name"] == "Northern Watch"
        assert response.data["date_range"]["start"] == "2025-10-01"
        assert response.data["date_range"]["end"] == "2025-10-03"
        assert response.data["summary"]["total_days"] == 3
        assert response.data["summary"]["total_feet_built"] == "45.00"
        assert response.data["summary"]["total_ice_cubic_yards"] == "8775.00"
        assert response.data["summary"]["total_cost_gold_dragons"] == "16672500.00"
        assert response.data["summary"]["average_feet_per_day"] == "15.00"
        assert response.data["summary"]["average_cost_per_day"] == "5557500.00"
        assert len(response.data["daily_breakdown"]) == 3

    def test_cost_overview_no_data_for_range(self, api_client: APIClient) -> None:
        """Test cost overview when no progress exists for given date range."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        url = reverse("profile-cost-overview", kwargs={"pk": profile.id})
        response = api_client.get(url, {"start_date": "2025-10-01", "end_date": "2025-10-15"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["summary"]["total_feet_built"] == "0.00"
        assert response.data["summary"]["total_ice_cubic_yards"] == "0.00"
        assert response.data["summary"]["total_cost_gold_dragons"] == "0.00"
        assert response.data["summary"]["average_feet_per_day"] == "0.00"
        assert response.data["summary"]["average_cost_per_day"] == "0.00"
        assert response.data["daily_breakdown"] == []

    def test_cost_overview_invalid_profile(self, api_client: APIClient) -> None:
        """Test cost overview with non-existent profile returns 404."""
        url = reverse("profile-cost-overview", kwargs={"pk": 9999})
        response = api_client.get(url, {"start_date": "2025-10-01", "end_date": "2025-10-15"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cost_overview_missing_start_date_param(self, api_client: APIClient) -> None:
        """Test cost overview without start_date parameter returns 400."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        url = reverse("profile-cost-overview", kwargs={"pk": profile.id})
        response = api_client.get(url, {"end_date": "2025-10-15"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cost_overview_missing_end_date_param(self, api_client: APIClient) -> None:
        """Test cost overview without end_date parameter returns 400."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        url = reverse("profile-cost-overview", kwargs={"pk": profile.id})
        response = api_client.get(url, {"start_date": "2025-10-01"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cost_overview_invalid_date_format(self, api_client: APIClient) -> None:
        """Test cost overview with invalid date format returns 400."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        url = reverse("profile-cost-overview", kwargs={"pk": profile.id})
        response = api_client.get(url, {"start_date": "2025/10/01", "end_date": "2025-10-15"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_cost_overview_success(self, api_client: APIClient) -> None:
        """Test bulk cost overview endpoint processes multiple profiles in parallel."""
        profile1 = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        profile2 = Profile.objects.create(name="Eastern Defense", team_lead="Tormund")
        section1 = WallSection.objects.create(
            profile=profile1,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )
        section2 = WallSection.objects.create(
            profile=profile2,
            section_name="Tower 5-6",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        DailyProgress.objects.create(
            wall_section=section1,
            date=date(2025, 10, 1),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )
        DailyProgress.objects.create(
            wall_section=section2,
            date=date(2025, 10, 1),
            feet_built=Decimal("20.00"),
            ice_cubic_yards=Decimal("3900.00"),
            cost_gold_dragons=Decimal("7410000.00"),
        )

        url = reverse("profile-bulk-cost-overview")
        response = api_client.get(
            url,
            {
                "profile_ids": f"{profile1.id},{profile2.id}",
                "start_date": "2025-10-01",
                "end_date": "2025-10-01",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        profile_ids = {r["profile_id"] for r in response.data["results"]}
        assert profile_ids == {profile1.id, profile2.id}

    def test_bulk_cost_overview_single_profile(self, api_client: APIClient) -> None:
        """Test bulk cost overview with single profile."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        DailyProgress.objects.create(
            wall_section=section,
            date=date(2025, 10, 1),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )

        url = reverse("profile-bulk-cost-overview")
        response = api_client.get(
            url,
            {"profile_ids": str(profile.id), "start_date": "2025-10-01", "end_date": "2025-10-01"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["profile_id"] == profile.id
        assert response.data["results"][0]["total_feet_built"] == "10.00"

    def test_bulk_cost_overview_missing_profile_ids(self, api_client: APIClient) -> None:
        """Test bulk cost overview without profile_ids parameter returns 400."""
        url = reverse("profile-bulk-cost-overview")
        response = api_client.get(url, {"start_date": "2025-10-01", "end_date": "2025-10-01"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_cost_overview_missing_start_date(self, api_client: APIClient) -> None:
        """Test bulk cost overview without start_date parameter returns 400."""
        url = reverse("profile-bulk-cost-overview")
        response = api_client.get(url, {"profile_ids": "1,2", "end_date": "2025-10-01"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_cost_overview_missing_end_date(self, api_client: APIClient) -> None:
        """Test bulk cost overview without end_date parameter returns 400."""
        url = reverse("profile-bulk-cost-overview")
        response = api_client.get(url, {"profile_ids": "1,2", "start_date": "2025-10-01"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_progress_via_profile_success(self, api_client: APIClient) -> None:
        """Test creating progress via profile nested endpoint returns 201 with auto-calculated values."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        url = reverse("profile-create-progress", kwargs={"pk": profile.id})
        payload = {
            "wall_section_id": wall_section.id,
            "date": "2025-10-15",
            "feet_built": 12.5,
            "notes": "Clear weather, good progress",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data
        assert response.data["wall_section"] == wall_section.id
        assert response.data["date"] == "2025-10-15"
        assert response.data["feet_built"] == "12.50"
        assert response.data["ice_cubic_yards"] == "2437.50"
        assert response.data["cost_gold_dragons"] == "4631250.00"
        assert response.data["notes"] == "Clear weather, good progress"
        assert "created_at" in response.data

    def test_create_progress_via_profile_validates_wall_section_ownership(self, api_client: APIClient) -> None:
        """Test creating progress fails when wall_section does not belong to profile."""
        profile1 = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        profile2 = Profile.objects.create(name="Eastern Defense", team_lead="Tormund")
        wall_section = WallSection.objects.create(
            profile=profile2,
            section_name="Tower 5-6",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        url = reverse("profile-create-progress", kwargs={"pk": profile1.id})
        payload = {
            "wall_section_id": wall_section.id,
            "date": "2025-10-15",
            "feet_built": 12.5,
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "wall_section_id" in response.data

    def test_create_progress_via_profile_missing_wall_section_id(self, api_client: APIClient) -> None:
        """Test creating progress without wall_section_id returns 400."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        url = reverse("profile-create-progress", kwargs={"pk": profile.id})
        payload = {
            "date": "2025-10-15",
            "feet_built": 12.5,
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "wall_section_id" in response.data

    def test_create_progress_via_profile_invalid_date_format(self, api_client: APIClient) -> None:
        """Test creating progress with invalid date format returns 400."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        url = reverse("profile-create-progress", kwargs={"pk": profile.id})
        payload = {
            "wall_section_id": wall_section.id,
            "date": "2025/10/15",
            "feet_built": 12.5,
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "date" in response.data

    def test_create_progress_via_profile_auto_calculates_ice_and_cost(self, api_client: APIClient) -> None:
        """Test creating progress auto-calculates ice_cubic_yards and cost_gold_dragons."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        url = reverse("profile-create-progress", kwargs={"pk": profile.id})
        payload = {
            "wall_section_id": wall_section.id,
            "date": "2025-10-15",
            "feet_built": 10.0,
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["feet_built"] == "10.00"
        assert response.data["ice_cubic_yards"] == "1950.00"
        assert response.data["cost_gold_dragons"] == "3705000.00"
