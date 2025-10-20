"""URL configuration for profiles app."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.profiles.views import ProfileViewSet, WallSectionViewSet

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"wallsections", WallSectionViewSet, basename="wallsection")

urlpatterns = [
    path("", include(router.urls)),
]
