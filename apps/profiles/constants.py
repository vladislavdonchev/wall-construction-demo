"""Centralized constants for wall construction calculations."""

from __future__ import annotations

from decimal import Decimal

# Wall construction constants
ICE_PER_FOOT = Decimal("195")  # cubic yards per linear foot
COST_PER_CUBIC_YARD = Decimal("1900")  # Gold Dragons per cubic yard
TARGET_HEIGHT = 30  # feet - maximum wall height

# Validation limits
MAX_HEIGHT = 30  # Maximum height for wall sections (must match TARGET_HEIGHT)
MIN_HEIGHT = 0  # Minimum height for wall sections
MAX_TEAMS = 100  # Maximum number of parallel construction teams
MIN_TEAMS = 1  # Minimum number of parallel construction teams
MAX_PROFILES = 100  # Maximum number of profiles per simulation
MAX_SECTIONS_PER_PROFILE = 2000  # Maximum sections in a single profile
MAX_TOTAL_SECTIONS = 10_000  # Maximum total sections across all profiles
