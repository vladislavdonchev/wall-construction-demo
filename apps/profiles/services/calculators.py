"""Calculator services for ice usage and cost calculations."""

from __future__ import annotations

from decimal import Decimal


class IceUsageCalculator:
    """Calculate ice usage and costs for wall construction."""

    ICE_PER_FOOT = Decimal("195")  # cubic yards per linear foot
    COST_PER_CUBIC_YARD = Decimal("1900")  # Gold Dragons per cubic yard

    def calculate_ice_usage(self, feet_built: Decimal) -> Decimal:
        """Calculate ice usage in cubic yards from feet built.

        Args:
            feet_built: Linear feet of wall built

        Returns:
            Ice usage in cubic yards (feet_built × 195)
        """
        return feet_built * self.ICE_PER_FOOT

    def calculate_daily_cost(self, ice_cubic_yards: Decimal) -> Decimal:
        """Calculate daily cost in Gold Dragons from ice usage.

        Args:
            ice_cubic_yards: Ice usage in cubic yards

        Returns:
            Daily cost in Gold Dragons (ice_cubic_yards × 1900)
        """
        return ice_cubic_yards * self.COST_PER_CUBIC_YARD
