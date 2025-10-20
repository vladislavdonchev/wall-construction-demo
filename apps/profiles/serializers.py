"""Serializers for Profile API."""

from __future__ import annotations

from rest_framework import serializers

from apps.profiles.models import Profile, WallSection


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
            "start_position",
            "target_length_feet",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
