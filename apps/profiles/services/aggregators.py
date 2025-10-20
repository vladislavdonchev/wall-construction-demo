"""Service for cost calculations across multiple profiles."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime

from apps.profiles.repositories import DailyProgressRepository


class CostAggregatorService:
    """Service for cost calculations across multiple profiles.

    Uses ThreadPoolExecutor with single worker for serial execution
    to maintain proper resource cleanup semantics while ensuring
    SQLite database compatibility.
    """

    def __init__(self) -> None:
        """Initialize service with single-threaded executor."""
        self.executor = ThreadPoolExecutor(max_workers=1)

    def calculate_multi_profile_costs(
        self,
        profile_ids: list[int],
        start_date: str,
        end_date: str,
    ) -> list[dict[str, int | str]]:
        """Calculate costs for multiple profiles.

        Args:
            profile_ids: List of profile IDs to process
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of cost summaries per profile

        Raises:
            ValueError: If date format is invalid
            Exception: Any exception raised during profile cost calculation
        """
        # Convert string dates to date objects (can raise ValueError)
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        futures = {
            self.executor.submit(
                self._calculate_profile_cost,
                profile_id,
                start_date_obj,
                end_date_obj,
            ): profile_id
            for profile_id in profile_ids
        }

        results = []
        for future in as_completed(futures):
            profile_id = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                raise RuntimeError(f"Failed to calculate costs for profile {profile_id}") from e

        return results

    def shutdown(self) -> None:
        """Shutdown the thread pool executor."""
        self.executor.shutdown(wait=True)

    def _calculate_profile_cost(
        self,
        profile_id: int,
        start_date_obj: date,
        end_date_obj: date,
    ) -> dict[str, int | str]:
        """Calculate cost summary for a single profile.

        Args:
            profile_id: Profile ID to calculate for
            start_date_obj: Start date object
            end_date_obj: End date object

        Returns:
            Dictionary with profile cost summary
        """
        repo = DailyProgressRepository()

        # Use Django ORM aggregation for efficient DB queries
        aggregates = repo.get_aggregates_by_profile(
            profile_id,
            start_date_obj,
            end_date_obj,
        )

        return {
            "profile_id": profile_id,
            "total_feet_built": str(aggregates["total_feet"]),
            "total_ice_cubic_yards": str(aggregates["total_ice"]),
            "total_cost_gold_dragons": str(aggregates["total_cost"]),
        }
