"""Views for Profile API."""

from __future__ import annotations

from rest_framework import viewsets

from apps.profiles.models import DailyProgress, Profile, WallSection
from apps.profiles.serializers import (
    DailyProgressSerializer,
    ProfileSerializer,
    WallSectionSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet[Profile]):
    """ViewSet for Profile CRUD operations."""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class WallSectionViewSet(viewsets.ModelViewSet[WallSection]):
    """ViewSet for WallSection CRUD operations."""

    queryset = WallSection.objects.all()
    serializer_class = WallSectionSerializer
    filterset_fields = ["profile"]


class DailyProgressViewSet(viewsets.ModelViewSet[DailyProgress]):
    """ViewSet for DailyProgress CRUD operations."""

    queryset = DailyProgress.objects.all()
    serializer_class = DailyProgressSerializer
    filterset_fields = ["wall_section", "date"]
