"""Unit tests for Profile API serializers."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from apps.profiles.models import DailyProgress, Profile, Simulation, WallSection
from apps.profiles.serializers import DailyProgressSerializer


@pytest.mark.django_db
class TestDailyProgressSerializer:
    """Test DailyProgressSerializer functionality."""

    def test_create_daily_progress_with_auto_calculation(self, simulation: Simulation) -> None:
        """Test serializer auto-calculates ice_cubic_yards and cost_gold_dragons."""
        profile = Profile.objects.create(simulation=simulation, name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
        )

        serializer = DailyProgressSerializer(
            data={
                "wall_section": wall_section.id,
                "date": "2025-10-15",
                "feet_built": "12.50",
                "notes": "Clear weather, good progress",
            }
        )

        assert serializer.is_valid(raise_exception=True)
        progress = serializer.save()

        # Verify calculations: 12.5 feet × 195 yd³/ft = 2437.5 yd³
        assert progress.ice_cubic_yards == Decimal("2437.50")
        # 2437.5 yd³ × 1900 GD/yd³ = 4,631,250 GD
        assert progress.cost_gold_dragons == Decimal("4631250.00")
        assert progress.feet_built == Decimal("12.50")
        assert progress.notes == "Clear weather, good progress"

    def test_serializer_output_includes_calculated_fields(self, simulation: Simulation) -> None:
        """Test serializer returns calculated fields in response."""
        profile = Profile.objects.create(simulation=simulation, name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
        )

        serializer = DailyProgressSerializer(
            data={
                "wall_section": wall_section.id,
                "date": "2025-10-15",
                "feet_built": "12.50",
            }
        )

        assert serializer.is_valid(raise_exception=True)
        progress = serializer.save()

        # Serialize the created object
        output_serializer = DailyProgressSerializer(progress)
        data = output_serializer.data

        assert data["feet_built"] == "12.50"
        assert data["ice_cubic_yards"] == "2437.50"
        assert data["cost_gold_dragons"] == "4631250.00"
        assert "id" in data
        assert "created_at" in data

    def test_create_daily_progress_without_notes(self, simulation: Simulation) -> None:
        """Test creating daily progress without optional notes field."""
        profile = Profile.objects.create(simulation=simulation, name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
        )

        serializer = DailyProgressSerializer(
            data={
                "wall_section": wall_section.id,
                "date": "2025-10-15",
                "feet_built": "10.00",
            }
        )

        assert serializer.is_valid(raise_exception=True)
        progress = serializer.save()

        assert progress.notes == ""
        assert progress.ice_cubic_yards == Decimal("1950.00")
        assert progress.cost_gold_dragons == Decimal("3705000.00")

    def test_create_daily_progress_for_zero_feet(self, simulation: Simulation) -> None:
        """Test creating daily progress with zero feet built."""
        profile = Profile.objects.create(simulation=simulation, name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
        )

        serializer = DailyProgressSerializer(
            data={
                "wall_section": wall_section.id,
                "date": "2025-10-15",
                "feet_built": "0.00",
            }
        )

        assert serializer.is_valid(raise_exception=True)
        progress = serializer.save()

        assert progress.ice_cubic_yards == Decimal("0.00")
        assert progress.cost_gold_dragons == Decimal("0.00")

    def test_calculated_fields_are_read_only(self, simulation: Simulation) -> None:
        """Test that ice_cubic_yards and cost_gold_dragons cannot be set via API."""
        profile = Profile.objects.create(simulation=simulation, name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
        )

        # Try to override calculated fields
        serializer = DailyProgressSerializer(
            data={
                "wall_section": wall_section.id,
                "date": "2025-10-15",
                "feet_built": "10.00",
                "ice_cubic_yards": "9999.99",  # Should be ignored
                "cost_gold_dragons": "9999999.99",  # Should be ignored
            }
        )

        assert serializer.is_valid(raise_exception=True)
        progress = serializer.save()

        # Verify calculated values are used, not provided values
        assert progress.ice_cubic_yards == Decimal("1950.00")
        assert progress.cost_gold_dragons == Decimal("3705000.00")

    def test_unique_constraint_validation(self, simulation: Simulation) -> None:
        """Test serializer validates unique constraint on wall_section + date."""
        profile = Profile.objects.create(simulation=simulation, name="Northern Watch", team_lead="Jon Snow")
        wall_section = WallSection.objects.create(
            profile=profile,
            section_name="Tower 1-2",
        )

        # Create first progress entry
        DailyProgress.objects.create(
            wall_section=wall_section,
            date=date(2025, 10, 15),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00"),
        )

        # Try to create duplicate
        serializer = DailyProgressSerializer(
            data={
                "wall_section": wall_section.id,
                "date": "2025-10-15",
                "feet_built": "5.00",
            }
        )

        # DRF validates unique constraints during is_valid()
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
