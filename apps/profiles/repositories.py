"""Repository layer for Profile app data access."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Avg, Count, QuerySet, Sum

from apps.profiles.models import DailyProgress


class DailyProgressRepository:
    """Data access layer for DailyProgress model."""

    def get_by_date(self, profile_id: int, target_date: date) -> QuerySet[DailyProgress]:
        """Retrieve all progress records for a profile on a specific date.

        Args:
            profile_id: Profile ID to filter by
            target_date: Date to retrieve progress for

        Returns:
            QuerySet of DailyProgress records with wall_section pre-fetched
        """
        return DailyProgress.objects.filter(wall_section__profile_id=profile_id, date=target_date).select_related("wall_section")

    def get_aggregates_by_profile(self, profile_id: int, start_date: date, end_date: date) -> dict[str, Decimal | int]:
        """Get aggregated statistics for a profile within date range.

        Args:
            profile_id: Profile ID to aggregate for
            start_date: Start date of range (inclusive)
            end_date: End date of range (inclusive)

        Returns:
            Dictionary with aggregated statistics:
                - total_feet: Sum of feet_built
                - total_ice: Sum of ice_cubic_yards
                - total_cost: Sum of cost_gold_dragons
                - avg_feet: Average feet_built per day
                - record_count: Number of records in range
        """
        result = DailyProgress.objects.filter(
            wall_section__profile_id=profile_id,
            date__gte=start_date,
            date__lte=end_date,
        ).aggregate(
            total_feet=Sum("feet_built"),
            total_ice=Sum("ice_cubic_yards"),
            total_cost=Sum("cost_gold_dragons"),
            avg_feet=Avg("feet_built"),
            record_count=Count("id"),
        )

        # Normalize all decimals to 2 decimal places
        two_places = Decimal("0.01")
        return {
            "total_feet": (Decimal("0") if result["total_feet"] is None else result["total_feet"]).quantize(two_places),
            "total_ice": (Decimal("0") if result["total_ice"] is None else result["total_ice"]).quantize(two_places),
            "total_cost": (Decimal("0") if result["total_cost"] is None else result["total_cost"]).quantize(two_places),
            "avg_feet": (Decimal("0") if result["avg_feet"] is None else result["avg_feet"]).quantize(two_places),
            "record_count": result["record_count"],
        }
