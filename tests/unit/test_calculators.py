"""Unit tests for calculator services."""

from __future__ import annotations

from decimal import Decimal

from apps.profiles.services.calculators import IceUsageCalculator


class TestIceUsageCalculator:
    """Test IceUsageCalculator service."""

    def test_calculate_ice_usage_for_10_feet(self) -> None:
        """Test ice usage calculation for 10 feet built."""
        calculator = IceUsageCalculator()
        result = calculator.calculate_ice_usage(Decimal("10.00"))

        # 10 feet × 195 yd³/ft = 1950 yd³
        assert result == Decimal("1950.00")

    def test_calculate_ice_usage_for_zero_feet(self) -> None:
        """Test ice usage calculation for zero feet built."""
        calculator = IceUsageCalculator()
        result = calculator.calculate_ice_usage(Decimal("0.00"))

        assert result == Decimal("0.00")

    def test_calculate_ice_usage_for_fractional_feet(self) -> None:
        """Test ice usage calculation for fractional feet."""
        calculator = IceUsageCalculator()
        result = calculator.calculate_ice_usage(Decimal("12.5"))

        # 12.5 feet × 195 yd³/ft = 2437.5 yd³
        assert result == Decimal("2437.50")

    def test_calculate_daily_cost_from_ice_usage(self) -> None:
        """Test daily cost calculation from ice usage."""
        calculator = IceUsageCalculator()
        ice_cubic_yards = Decimal("1950.00")
        result = calculator.calculate_daily_cost(ice_cubic_yards)

        # 1950 yd³ × 1900 GD/yd³ = 3,705,000 GD
        assert result == Decimal("3705000.00")

    def test_calculate_daily_cost_for_zero_ice(self) -> None:
        """Test daily cost calculation for zero ice usage."""
        calculator = IceUsageCalculator()
        result = calculator.calculate_daily_cost(Decimal("0.00"))

        assert result == Decimal("0.00")

    def test_full_calculation_pipeline(self) -> None:
        """Test complete calculation from feet to cost."""
        calculator = IceUsageCalculator()
        feet_built = Decimal("12.5")

        ice_usage = calculator.calculate_ice_usage(feet_built)
        daily_cost = calculator.calculate_daily_cost(ice_usage)

        # 12.5 feet × 195 yd³/ft = 2437.5 yd³
        assert ice_usage == Decimal("2437.50")
        # 2437.5 yd³ × 1900 GD/yd³ = 4,631,250 GD
        assert daily_cost == Decimal("4631250.00")
