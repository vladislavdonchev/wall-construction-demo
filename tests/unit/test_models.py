"""Unit tests for Profile models and repositories."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.profiles.constants import COST_PER_CUBIC_YARD, ICE_PER_FOOT
from apps.profiles.models import DailyProgress, Profile, WallSection


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
        )

        assert wall_section.id is not None
        assert wall_section.profile == profile
        assert wall_section.section_name == "Tower 1-2"

    def test_wall_section_str_representation(self) -> None:
        """Test wall section string representation."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
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
        )

        feet_built = Decimal("10.00")
        ice_cubic_yards = feet_built * ICE_PER_FOOT  # 10 × 195 = 1950
        cost_gold_dragons = ice_cubic_yards * COST_PER_CUBIC_YARD  # 1950 × 1900 = 3,705,000

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
        )

        progress = DailyProgress.objects.create(
            wall_section=wall_section,
            date=date(2025, 10, 20),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )

        assert str(progress) == "Tower 1-2: 10.00 ft on 2025-10-20"
