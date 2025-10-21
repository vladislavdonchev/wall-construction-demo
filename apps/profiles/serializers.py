"""Serializers for Profile API."""

from __future__ import annotations

from decimal import Decimal
from typing import cast

from rest_framework import serializers

from apps.profiles.constants import COST_PER_CUBIC_YARD, ICE_PER_FOOT
from apps.profiles.models import DailyProgress, Profile, Simulation, WallSection


class SimulationSerializer(serializers.ModelSerializer[Simulation]):
    """Serializer for Simulation model."""

    class Meta:
        model = Simulation
        fields = [
            "id",
            "config_text",
            "num_teams",
            "start_date",
            "total_days",
            "total_cost",
            "total_sections",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProfileSerializer(serializers.ModelSerializer[Profile]):
    """Serializer for Profile model."""

    class Meta:
        model = Profile
        fields = ["id", "name", "team_lead", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class WallSectionSerializer(serializers.ModelSerializer[WallSection]):
    """Serializer for WallSection model."""

    class Meta:
        model = WallSection
        fields = [
            "id",
            "profile",
            "section_name",
            "initial_height",
            "current_height",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DailyProgressSerializer(serializers.ModelSerializer[DailyProgress]):
    """Serializer for DailyProgress model with auto-calculation of ice and cost."""

    class Meta:
        model = DailyProgress
        fields = [
            "id",
            "wall_section",
            "date",
            "feet_built",
            "ice_cubic_yards",
            "cost_gold_dragons",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "ice_cubic_yards", "cost_gold_dragons", "created_at"]

    def create(self, validated_data: dict[str, object]) -> DailyProgress:
        """Create DailyProgress with auto-calculated ice_cubic_yards and cost_gold_dragons."""
        feet_built = cast(Decimal, validated_data["feet_built"])
        ice_cubic_yards = feet_built * ICE_PER_FOOT
        cost_gold_dragons = ice_cubic_yards * COST_PER_CUBIC_YARD

        validated_data["ice_cubic_yards"] = ice_cubic_yards
        validated_data["cost_gold_dragons"] = cost_gold_dragons

        return super().create(validated_data)


class ProfileWithSectionsSerializer(serializers.ModelSerializer[Profile]):
    """Serializer for Profile with nested WallSections."""

    wall_sections = WallSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "name", "team_lead", "wall_sections"]


class SimulationDetailSerializer(serializers.ModelSerializer[Simulation]):
    """Detailed serializer for Simulation with nested profiles and sections."""

    profiles = ProfileWithSectionsSerializer(many=True, read_only=True)

    class Meta:
        model = Simulation
        fields = [
            "id",
            "config_text",
            "num_teams",
            "start_date",
            "total_days",
            "total_cost",
            "total_sections",
            "created_at",
            "profiles",
        ]
        read_only_fields = ["id", "created_at"]
