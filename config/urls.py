"""URL configuration for Wall Construction API."""

from __future__ import annotations

from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    path("api/", include("apps.profiles.urls")),
]
