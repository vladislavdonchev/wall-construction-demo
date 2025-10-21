"""Mixin for simulation reporting and analytics."""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from apps.profiles.models import Profile
from apps.profiles.services.queries import ReportingQueries


class ReportingMixin:
    """Mixin providing reporting endpoints."""

    @action(detail=True, methods=["get"], url_path=r"days/(?P<day>\d+)")
    def days(self, _request: Request, pk: int, day: str) -> Response:
        """Get ice usage for profile on specific day number.

        Spec-compliant endpoint: GET /profiles/1/days/1/
        """
        profile = get_object_or_404(Profile, pk=pk)
        day_num = int(day)

        first_progress = ReportingQueries.get_first_progress_date(profile)
        if not first_progress:
            raise NotFound("No simulation data for this profile")

        total_feet, total_ice, sections = ReportingQueries.get_ice_usage_for_day(profile, day_num)

        return Response(
            {
                "day": day_num,
                "total_feet_built": str(total_feet),
                "total_ice_cubic_yards": str(total_ice),
                "sections": sections,
            }
        )

    @action(detail=True, methods=["get"], url_path=r"overview/(?P<day>\d+)")
    def overview_by_day(self, _request: Request, pk: int, day: str) -> Response:
        """Get cost overview for profile up to specific day number.

        Spec-compliant endpoint: GET /profiles/1/overview/1/
        """
        profile = get_object_or_404(Profile, pk=pk)
        day_num = int(day)

        first_progress = ReportingQueries.get_first_progress_date(profile)
        if not first_progress:
            raise NotFound("No simulation data for this profile")

        total_cost = ReportingQueries.get_cost_overview(None, profile, day_num)

        return Response(
            {
                "day": str(day_num),
                "cost": str(total_cost),
            }
        )

    @action(detail=False, methods=["get"], url_path=r"overview/(?P<day>\d+)")
    def overview_all_by_day(self, _request: Request, day: str) -> Response:
        """Get total cost for all profiles up to specific day number.

        Spec-compliant endpoint: GET /profiles/overview/1/
        """
        day_num = int(day)

        first_progress = ReportingQueries.get_first_progress_date(None)
        if not first_progress:
            raise NotFound("No simulation data")

        total_cost = ReportingQueries.get_cost_overview(None, None, day_num)

        return Response(
            {
                "day": str(day_num),
                "cost": str(total_cost),
            }
        )

    @action(detail=False, methods=["get"], url_path="overview")
    def overview_total(self, _request: Request) -> Response:
        """Get total cost and days for entire construction.

        Spec-compliant endpoint: GET /profiles/overview/
        """
        total_cost = ReportingQueries.get_cost_overview(None, None, None)
        total_days = ReportingQueries.get_total_days(None, None)

        return Response(
            {
                "day": total_days,
                "cost": str(total_cost),
            }
        )
