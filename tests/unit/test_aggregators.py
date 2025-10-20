"""Unit tests for CostAggregatorService."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from apps.profiles.models import DailyProgress, Profile, WallSection
from apps.profiles.services.aggregators import CostAggregatorService


@pytest.mark.django_db
class TestCostAggregatorService:
    """Test CostAggregatorService cost calculations."""

    def test_calculate_multi_profile_costs_single_profile(self) -> None:
        """Test calculating costs for a single profile."""
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

        aggregator = CostAggregatorService()
        results = aggregator.calculate_multi_profile_costs([profile.id], "2025-10-01", "2025-10-01")
        aggregator.shutdown()

        assert len(results) == 1
        assert results[0]["profile_id"] == profile.id
        assert results[0]["total_feet_built"] == "10.00"
        assert results[0]["total_ice_cubic_yards"] == "1950.00"
        assert results[0]["total_cost_gold_dragons"] == "3705000.00"

    def test_calculate_multi_profile_costs_multiple_profiles(self) -> None:
        """Test calculating costs for multiple profiles."""
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

        aggregator = CostAggregatorService()
        results = aggregator.calculate_multi_profile_costs([profile1.id, profile2.id], "2025-10-01", "2025-10-01")
        aggregator.shutdown()

        assert len(results) == 2
        profile_ids = {r["profile_id"] for r in results}
        assert profile_ids == {profile1.id, profile2.id}

    def test_calculate_multi_profile_costs_no_data(self) -> None:
        """Test calculating costs when no progress data exists."""
        profile = Profile.objects.create(name="Northern Watch", team_lead="Jon Snow")

        aggregator = CostAggregatorService()
        results = aggregator.calculate_multi_profile_costs([profile.id], "2025-10-01", "2025-10-01")
        aggregator.shutdown()

        assert len(results) == 1
        assert results[0]["total_feet_built"] == "0"
        assert results[0]["total_ice_cubic_yards"] == "0"
        assert results[0]["total_cost_gold_dragons"] == "0"
