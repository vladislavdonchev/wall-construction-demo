"""ViewSets for Profile CRUD operations."""

from __future__ import annotations

from rest_framework import viewsets

from apps.profiles.models import DailyProgress, Profile, WallSection
from apps.profiles.serializers import (
    DailyProgressSerializer,
    ProfileSerializer,
    WallSectionSerializer,
)
from apps.profiles.views.reporting_views import ReportingMixin
from apps.profiles.views.simulation_views import SimulationMixin


class ProfileViewSet(SimulationMixin, ReportingMixin, viewsets.ModelViewSet[Profile]):
    """ViewSet for Profile CRUD and custom actions (simulation, reporting)."""

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
