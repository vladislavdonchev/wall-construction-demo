"""Pytest configuration and fixtures for Wall Construction API."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.profiles.models import Simulation


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db: object) -> None:
    """Enable database access for all tests with proper transaction isolation."""


@pytest.fixture
def api_client() -> APIClient:
    """Provide DRF API client for testing."""
    return APIClient()


@pytest.fixture
def simulation() -> Simulation:
    """Provide a test simulation instance."""
    return Simulation.objects.create(
        config_text="21 25 28",
        num_teams=4,
        start_date=date(2025, 1, 1),
        total_days=30,
        total_cost=Decimal("1000000.00"),
        total_sections=3,
    )
