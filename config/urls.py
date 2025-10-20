"""URL configuration for Wall Construction API."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("api/", include("apps.profiles.urls")),
]
