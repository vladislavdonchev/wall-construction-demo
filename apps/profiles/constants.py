"""Centralized constants for wall construction calculations."""

from __future__ import annotations

from decimal import Decimal

ICE_PER_FOOT = Decimal("195")  # cubic yards per linear foot
COST_PER_CUBIC_YARD = Decimal("1900")  # Gold Dragons per cubic yard
TARGET_HEIGHT = 30  # feet - maximum wall height
