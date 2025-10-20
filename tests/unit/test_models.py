"""Unit tests for Profile models and repositories."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.profiles.models import DailyProgress, Profile, WallSection
from apps.profiles.repositories import DailyProgressRepository


@pytest.mark.django_db
class TestProfileModel:
    """Test Profile model functionality."""

    def test_create_profile_success(self) -> None:
        """Test creating a profile with valid data."""
        profile = Profile.objects.create(
            name="Northern Watch",
            team_lead="Jon Snow",
            is_active=True,
        )

        assert profile.id is not None
        assert profile.name == "Northern Watch"
        assert profile.team_lead == "Jon Snow"
        assert profile.is_active is True
        assert profile.created_at is not None
        assert profile.updated_at is not None

    def test_profile_name_unique(self) -> None:
        """Test profile name must be unique."""
        Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        with pytest.raises(IntegrityError):
            Profile.objects.create(name="Northern Watch", team_lead="Samwell Tarly")

    def test_profile_str_representation(self) -> None:
        """Test profile string representation."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        assert str(profile) == "Northern Watch (led by Jon Snow)"


@pytest.mark.django_db
class TestWallSectionModel:
    """Test WallSection model functionality."""

    def test_create_wall_section_success(self) -> None:
        """Test creating a wall section with valid data."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        assert wall_section.id is not None
        assert wall_section.profile == profile
        assert wall_section.section_name == "Tower 1-2"
        assert wall_section.start_position == Decimal("0.00")
        assert wall_section.target_length_feet == Decimal("500.00")

    def test_wall_section_str_representation(self) -> None:
        """Test wall section string representation."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        assert str(wall_section) == "Tower 1-2 (Northern Watch)"


@pytest.mark.django_db
class TestDailyProgressModel:
    """Test DailyProgress model functionality."""

    def test_create_daily_progress_with_calculated_values(self) -> None:
        """Test creating daily progress with explicitly calculated ice and cost values."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        feet_built = Decimal("10.00")
        ice_cubic_yards = feet_built * DailyProgress.ICE_PER_FOOT  # 10 × 195 = 1950
        cost_gold_dragons = ice_cubic_yards * DailyProgress.COST_PER_CUBIC_YARD  # 1950 × 1900 = 3,705,000

        progress = DailyProgress.objects.create(
            wall_section=wall_section,
            date=date(2025, 10, 20),
            feet_built=feet_built,
            ice_cubic_yards=ice_cubic_yards,
            cost_gold_dragons=cost_gold_dragons,
        )

        assert progress.ice_cubic_yards == Decimal("1950.00")
        assert progress.cost_gold_dragons == Decimal("3705000.00")

    def test_daily_progress_unique_per_wall_section_and_date(self) -> None:
        """Test only one progress entry allowed per wall section per day."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        DailyProgress.objects.create(
            wall_section=wall_section,
            date=date(2025, 10, 20),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )

        with pytest.raises(IntegrityError):
            DailyProgress.objects.create(
                wall_section=wall_section,
                date=date(2025, 10, 20),
                feet_built=Decimal("5.00"),
                ice_cubic_yards=Decimal("975.00"),
                cost_gold_dragons=Decimal("1852500.00"),
            )

    def test_daily_progress_str_representation(self) -> None:
        """Test daily progress string representation."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        progress = DailyProgress.objects.create(
            wall_section=wall_section,
            date=date(2025, 10, 20),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )

        assert str(progress) == "Tower 1-2: 10.00 ft on 2025-10-20"


@pytest.mark.django_db
class TestDailyProgressRepository:
    """Test DailyProgressRepository data access methods."""

    def test_get_by_date_returns_progress_for_profile_and_date(self) -> None:
        """Test retrieving all progress records for a profile on a specific date."""
        repo = DailyProgressRepository()
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
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

        results = repo.get_by_date(profile.id, target_date)

        assert results.count() == 2
        assert all(r.date == target_date for r in results)
        assert all(r.wall_section.profile_id == profile.id for r in results)

    def test_get_by_date_returns_empty_when_no_data(self) -> None:
        """Test get_by_date returns empty queryset when no progress exists."""
        repo = DailyProgressRepository()
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        target_date = date(2025, 10, 15)

        results = repo.get_by_date(profile.id, target_date)

        assert results.count() == 0

    def test_get_by_date_filters_by_profile(self) -> None:
        """Test get_by_date only returns progress for specified profile."""
        repo = DailyProgressRepository()
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
            feet_built=Decimal("20.00"),
            ice_cubic_yards=Decimal("3900.00"),
            cost_gold_dragons=Decimal("7410000.00"),
        )

        results = repo.get_by_date(profile1.id, target_date)

        assert results.count() == 1
        first_result = results.first()
        assert first_result is not None
        assert first_result.wall_section.profile_id == profile1.id

    def test_get_aggregates_by_profile_returns_summary_stats(self) -> None:
        """Test aggregated statistics for a profile within date range."""
        repo = DailyProgressRepository()
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

        result = repo.get_aggregates_by_profile(profile.id, date(2025, 10, 1), date(2025, 10, 3))

        assert result["total_feet"] == Decimal("45.00")
        assert result["total_ice"] == Decimal("8775.00")
        assert result["total_cost"] == Decimal("16672500.00")
        assert result["avg_feet"] == Decimal("15.00")
        assert result["record_count"] == 3

    def test_get_aggregates_by_profile_filters_date_range(self) -> None:
        """Test aggregates only include data within specified date range."""
        repo = DailyProgressRepository()
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00"),
        )

        DailyProgress.objects.create(
            wall_section=section,
            date=date(2025, 9, 30),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )
        DailyProgress.objects.create(
            wall_section=section,
            date=date(2025, 10, 1),
            feet_built=Decimal("15.00"),
            ice_cubic_yards=Decimal("2925.00"),
            cost_gold_dragons=Decimal("5557500.00"),
        )
        DailyProgress.objects.create(
            wall_section=section,
            date=date(2025, 10, 4),
            feet_built=Decimal("20.00"),
            ice_cubic_yards=Decimal("3900.00"),
            cost_gold_dragons=Decimal("7410000.00"),
        )

        result = repo.get_aggregates_by_profile(profile.id, date(2025, 10, 1), date(2025, 10, 3))

        assert result["total_feet"] == Decimal("15.00")
        assert result["record_count"] == 1

    def test_get_aggregates_by_profile_returns_zeros_when_no_data(self) -> None:
        """Test aggregates return explicit zeros when no data exists."""
        repo = DailyProgressRepository()
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        result = repo.get_aggregates_by_profile(profile.id, date(2025, 10, 1), date(2025, 10, 15))

        assert result["total_feet"] == Decimal("0")
        assert result["total_ice"] == Decimal("0")
        assert result["total_cost"] == Decimal("0")
        assert result["avg_feet"] == Decimal("0")
        assert result["record_count"] == 0

    def test_get_aggregates_by_profile_filters_by_profile(self) -> None:
        """Test aggregates only include data for specified profile."""
        repo = DailyProgressRepository()
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

        target_date = date(2025, 10, 1)
        DailyProgress.objects.create(
            wall_section=section1,
            date=target_date,
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )
        DailyProgress.objects.create(
            wall_section=section2,
            date=target_date,
            feet_built=Decimal("50.00"),
            ice_cubic_yards=Decimal("9750.00"),
            cost_gold_dragons=Decimal("18525000.00"),
        )

        result = repo.get_aggregates_by_profile(profile1.id, target_date, target_date)

        assert result["total_feet"] == Decimal("10.00")
        assert result["record_count"] == 1
