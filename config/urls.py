"""URL configuration for Wall Construction API."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("apps.profiles.urls")),
]
