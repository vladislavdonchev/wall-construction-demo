"""Pytest configuration and fixtures for Wall Construction API."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db: object) -> None:
    """Enable database access for all tests with proper transaction isolation."""


@pytest.fixture
def api_client() -> APIClient:
    """Provide DRF API client for testing."""
    return APIClient()
