"""Views for Profile API."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.profiles.models import DailyProgress, Profile, WallSection
from apps.profiles.parsers import ConfigParser
from apps.profiles.serializers import (
    DailyProgressSerializer,
    ProfileSerializer,
    WallSectionSerializer,
)
from apps.profiles.services.simulator import WallSimulator


class ProfileViewSet(viewsets.ModelViewSet[Profile]):
    """ViewSet for Profile CRUD operations."""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False, methods=["post"], url_path="simulate")
    def simulate(self, request: Request) -> Response:
        """Trigger wall construction simulation from config.

        Body:
            {
                "config": "21 25 28\\n17\\n17 22 17 19 17",
                "num_teams": 4,
                "start_date": "2025-10-20"
            }
        """
        config_text = request.data.get("config")
        num_teams = request.data.get("num_teams", 4)
        start_date_str = request.data.get("start_date")

        if not config_text:
            return Response(
                {"error": "config parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else date.today()
        except ValueError:
            return Response(
                {"error": "start_date must be in YYYY-MM-DD format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            num_teams = int(num_teams)
            if num_teams < 1:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "num_teams must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        parser = ConfigParser()
        try:
            profiles_config = parser.parse_config(config_text)
        except ValueError as e:
            return Response(
                {"error": f"Invalid config format: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for i, profile_config in enumerate(profiles_config, 1):
            profile_config.name = f"Profile {i}"
            profile_config.team_lead = f"Team Lead {i}"

        simulator = WallSimulator(num_teams=num_teams)
        result = simulator.simulate(profiles_config, start_date)

        return Response(result.model_dump(), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path=r"days/(?P<day>\d+)")
    def days(self, _request: Request, pk: int, day: str) -> Response:
        """Get ice usage for profile on specific day number.

        Spec-compliant endpoint: GET /profiles/1/days/1/
        """
        profile = get_object_or_404(Profile, pk=pk)
        day_num = int(day)

        first_progress = DailyProgress.objects.filter(wall_section__profile=profile).order_by("date").first()

        if not first_progress:
            return Response(
                {"error": "No simulation data for this profile"},
                status=status.HTTP_404_NOT_FOUND,
            )

        target_date = first_progress.date + timedelta(days=day_num - 1)

        wall_sections = WallSection.objects.filter(profile=profile)
        daily_progress = DailyProgress.objects.filter(wall_section__in=wall_sections, date=target_date)

        aggregates = daily_progress.aggregate(total_ice=Sum("ice_cubic_yards"))
        total_ice = Decimal("0.00") if aggregates["total_ice"] is None else aggregates["total_ice"]

        return Response(
            {
                "day": str(day_num),
                "ice_amount": str(total_ice),
            }
        )

    @action(detail=True, methods=["get"], url_path=r"overview/(?P<day>\d+)")
    def overview_by_day(self, _request: Request, pk: int, day: str) -> Response:
        """Get cost overview for profile up to specific day number.

        Spec-compliant endpoint: GET /profiles/1/overview/1/
        """
        profile = get_object_or_404(Profile, pk=pk)
        day_num = int(day)

        first_progress = DailyProgress.objects.filter(wall_section__profile=profile).order_by("date").first()

        if not first_progress:
            return Response(
                {"error": "No simulation data for this profile"},
                status=status.HTTP_404_NOT_FOUND,
            )

        end_date = first_progress.date + timedelta(days=day_num - 1)

        wall_sections = WallSection.objects.filter(profile=profile)
        daily_progress = DailyProgress.objects.filter(wall_section__in=wall_sections, date__lte=end_date)

        aggregates = daily_progress.aggregate(total_cost=Sum("cost_gold_dragons"))
        total_cost = Decimal("0.00") if aggregates["total_cost"] is None else aggregates["total_cost"]

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

        first_progress = DailyProgress.objects.order_by("date").first()

        if not first_progress:
            return Response(
                {"error": "No simulation data"},
                status=status.HTTP_404_NOT_FOUND,
            )

        end_date = first_progress.date + timedelta(days=day_num - 1)

        daily_progress = DailyProgress.objects.filter(date__lte=end_date)

        aggregates = daily_progress.aggregate(total_cost=Sum("cost_gold_dragons"))
        total_cost = Decimal("0.00") if aggregates["total_cost"] is None else aggregates["total_cost"]

        return Response(
            {
                "day": str(day_num),
                "cost": str(total_cost),
            }
        )

    @action(detail=False, methods=["get"], url_path="overview")
    def overview_total(self, _request: Request) -> Response:
        """Get total cost for entire construction.

        Spec-compliant endpoint: GET /profiles/overview/
        """
        daily_progress = DailyProgress.objects.all()

        aggregates = daily_progress.aggregate(total_cost=Sum("cost_gold_dragons"))
        total_cost = Decimal("0.00") if aggregates["total_cost"] is None else aggregates["total_cost"]

        return Response(
            {
                "day": None,
                "cost": str(total_cost),
            }
        )


class WallSectionViewSet(viewsets.ModelViewSet[WallSection]):
    """ViewSet for WallSection CRUD operations."""

    queryset = WallSection.objects.all()
    serializer_class = WallSectionSerializer
    filterset_fields = ["profile"]


class DailyProgressViewSet(viewsets.ModelViewSet[DailyProgress]):
    """ViewSet for DailyProgress CRUD operations."""

    queryset = DailyProgress.objects.all()
    serializer_class = DailyProgressSerializer
    filterset_fields = ["wall_section", "date"]
