"""URL configuration for profiles app."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.profiles.views.profile_views import (
    DailyProgressViewSet,
    ProfileViewSet,
    WallSectionViewSet,
)
from apps.profiles.views.simulations import SimulationViewSet

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"wallsections", WallSectionViewSet, basename="wallsection")
router.register(r"progress", DailyProgressViewSet, basename="dailyprogress")
router.register(r"simulations", SimulationViewSet, basename="simulation")

urlpatterns = [
    path("", include(router.urls)),
]
