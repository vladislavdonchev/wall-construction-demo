"""URL configuration for profiles app."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.profiles.views import (
    DailyProgressViewSet,
    ProfileViewSet,
    WallSectionViewSet,
)

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"wallsections", WallSectionViewSet, basename="wallsection")
router.register(r"progress", DailyProgressViewSet, basename="dailyprogress")

urlpatterns = [
    path("", include(router.urls)),
]
