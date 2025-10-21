"""Query services for reporting endpoints."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import QuerySet, Sum

from apps.profiles.models import DailyProgress, Profile, WallSection


class ReportingQueries:
    """Service class for reporting-related database queries."""

    @staticmethod
    def get_first_progress_date(profile: Profile | None = None) -> DailyProgress | None:
        """Get the first progress record for a profile or globally.

        Args:
            profile: Optional profile to filter by

        Returns:
            First DailyProgress record or None
        """
        if profile:
            return DailyProgress.objects.filter(wall_section__profile=profile).order_by("date").first()
        return DailyProgress.objects.order_by("date").first()

    @staticmethod
    def get_ice_usage_for_day(
        profile: Profile,
        day_num: int,
    ) -> tuple[Decimal, Decimal, list[dict[str, str]]]:
        """Get ice usage breakdown for a specific day.

        Args:
            profile: Profile to query
            day_num: Day number (1-indexed)

        Returns:
            Tuple of (total_feet, total_ice, sections_list)
        """
        first_progress = ReportingQueries.get_first_progress_date(profile)
        if not first_progress:
            return Decimal("0.00"), Decimal("0.00"), []

        target_date = first_progress.date + timedelta(days=day_num - 1)

        wall_sections = WallSection.objects.filter(profile=profile)
        daily_progress = DailyProgress.objects.filter(wall_section__in=wall_sections, date=target_date).select_related("wall_section")

        aggregates = daily_progress.aggregate(total_feet=Sum("feet_built"), total_ice=Sum("ice_cubic_yards"))
        total_feet = Decimal("0.00") if aggregates["total_feet"] is None else aggregates["total_feet"]
        total_ice = Decimal("0.00") if aggregates["total_ice"] is None else aggregates["total_ice"]

        sections = [
            {
                "section_name": progress.wall_section.section_name,
                "feet_built": str(progress.feet_built),
                "ice_cubic_yards": str(progress.ice_cubic_yards),
            }
            for progress in daily_progress
        ]

        return total_feet, total_ice, sections

    @staticmethod
    def get_cost_overview(
        profile: Profile | None,
        day_num: int | None,
    ) -> Decimal:
        """Get total cost for profile(s) up to a specific day.

        Args:
            profile: Optional profile to filter by (None = all profiles)
            day_num: Optional day number to limit (None = all days)

        Returns:
            Total cost in Gold Dragons
        """
        first_progress = ReportingQueries.get_first_progress_date(profile)
        if not first_progress:
            return Decimal("0.00")

        progress_qs: QuerySet[DailyProgress]

        if profile and day_num:
            end_date = first_progress.date + timedelta(days=day_num - 1)
            wall_sections = WallSection.objects.filter(profile=profile)
            progress_qs = DailyProgress.objects.filter(wall_section__in=wall_sections, date__lte=end_date)
        elif profile:
            wall_sections = WallSection.objects.filter(profile=profile)
            progress_qs = DailyProgress.objects.filter(wall_section__in=wall_sections)
        elif day_num:
            end_date = first_progress.date + timedelta(days=day_num - 1)
            progress_qs = DailyProgress.objects.filter(date__lte=end_date)
        else:
            progress_qs = DailyProgress.objects.all()

        aggregates = progress_qs.aggregate(total_cost=Sum("cost_gold_dragons"))
        return Decimal("0.00") if aggregates["total_cost"] is None else aggregates["total_cost"]

    @staticmethod
    def get_total_days(profile: Profile | None = None) -> int:
        """Calculate total construction days from progress data.

        Args:
            profile: Optional profile to filter by (None = all profiles)

        Returns:
            Total number of construction days (0 if no data)
        """
        first_progress = ReportingQueries.get_first_progress_date(profile)
        if not first_progress:
            return 0

        if profile:
            last_progress = DailyProgress.objects.filter(wall_section__profile=profile).order_by("-date").first()
        else:
            last_progress = DailyProgress.objects.order_by("-date").first()

        if not last_progress:
            return 0

        return (last_progress.date - first_progress.date).days + 1
