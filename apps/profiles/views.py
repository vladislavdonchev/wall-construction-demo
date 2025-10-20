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
from apps.profiles.repositories import DailyProgressRepository
from apps.profiles.serializers import (
    DailyProgressSerializer,
    ProfileSerializer,
    WallSectionSerializer,
)
from apps.profiles.services.aggregators import CostAggregatorService
from apps.profiles.services.simulator import WallSimulator


class ProfileViewSet(viewsets.ModelViewSet[Profile]):
    """ViewSet for Profile CRUD operations."""

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=True, methods=["get"], url_path="daily-ice-usage")
    def daily_ice_usage(self, request: Request, pk: int) -> Response:
        """Get daily ice usage aggregated by profile for a specific date."""
        profile = get_object_or_404(Profile, pk=pk)
        target_date = request.query_params.get("date")

        if not target_date:
            return Response(
                {"error": "date parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            return Response(
                {"error": "date must be in YYYY-MM-DD format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get all wall sections for this profile
        wall_sections = WallSection.objects.filter(profile=profile)

        # Get daily progress for all sections on target date
        daily_progress = DailyProgress.objects.filter(wall_section__in=wall_sections, date=target_date)

        # Aggregate totals
        aggregates = daily_progress.aggregate(
            total_feet=Sum("feet_built"),
            total_ice=Sum("ice_cubic_yards"),
        )

        # Explicit None checking with ternary operators
        total_feet_built = Decimal("0.00") if aggregates["total_feet"] is None else aggregates["total_feet"]
        total_ice_cubic_yards = Decimal("0.00") if aggregates["total_ice"] is None else aggregates["total_ice"]

        # Build section breakdown
        sections = []
        for progress in daily_progress:
            sections.append(
                {
                    "section_name": progress.wall_section.section_name,
                    "feet_built": str(progress.feet_built),
                    "ice_cubic_yards": str(progress.ice_cubic_yards),
                }
            )

        return Response(
            {
                "profile_id": profile.id,
                "profile_name": profile.name,
                "date": target_date,
                "total_feet_built": str(total_feet_built),
                "total_ice_cubic_yards": str(total_ice_cubic_yards),
                "sections": sections,
            }
        )

    @action(detail=True, methods=["get"], url_path="cost-overview")
    def cost_overview(self, request: Request, pk: int) -> Response:
        """Get cost overview for a profile within a date range."""
        profile = get_object_or_404(Profile, pk=pk)
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        if not start_date_str:
            return Response(
                {"error": "start_date parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not end_date_str:
            return Response(
                {"error": "end_date parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate date formats (YYYY-MM-DD)
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "start_date must be in YYYY-MM-DD format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "end_date must be in YYYY-MM-DD format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get aggregated statistics using repository
        repo = DailyProgressRepository()
        aggregates = repo.get_aggregates_by_profile(profile.id, start_date, end_date)

        # Calculate total days in range
        total_days = (end_date - start_date).days + 1

        # Calculate average cost per day
        total_cost = Decimal(str(aggregates["total_cost"]))
        record_count = aggregates["record_count"]
        average_cost_per_day = (total_cost / record_count).quantize(Decimal("0.01")) if record_count > 0 else Decimal("0.00")

        # Build daily breakdown - only include days with actual progress
        daily_breakdown = []
        current_date = start_date
        while current_date <= end_date:
            day_progress = repo.get_by_date(profile.id, current_date)
            if day_progress.exists():
                day_aggregates = day_progress.aggregate(
                    total_feet=Sum("feet_built"),
                    total_ice=Sum("ice_cubic_yards"),
                    total_cost=Sum("cost_gold_dragons"),
                )
                # Since day_progress.exists() is True, aggregates cannot be None
                daily_breakdown.append(
                    {
                        "date": current_date.isoformat(),
                        "feet_built": str(day_aggregates["total_feet"]),
                        "ice_cubic_yards": str(day_aggregates["total_ice"]),
                        "cost_gold_dragons": str(day_aggregates["total_cost"]),
                    }
                )
            current_date += timedelta(days=1)

        return Response(
            {
                "profile_id": profile.id,
                "profile_name": profile.name,
                "date_range": {
                    "start": start_date_str,
                    "end": end_date_str,
                },
                "summary": {
                    "total_days": total_days,
                    "total_feet_built": str(aggregates["total_feet"]),
                    "total_ice_cubic_yards": str(aggregates["total_ice"]),
                    "total_cost_gold_dragons": str(aggregates["total_cost"]),
                    "average_feet_per_day": str(aggregates["avg_feet"]),
                    "average_cost_per_day": str(average_cost_per_day),
                },
                "daily_breakdown": daily_breakdown,
            }
        )

    @action(detail=False, methods=["get"], url_path="bulk-cost-overview")
    def bulk_cost_overview(self, request: Request) -> Response:
        """Calculate costs for multiple profiles."""
        profile_ids_str = request.query_params.get("profile_ids")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not profile_ids_str:
            return Response(
                {"error": "profile_ids parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not start_date:
            return Response(
                {"error": "start_date parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not end_date:
            return Response(
                {"error": "end_date parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse comma-separated profile IDs
        try:
            profile_ids = [int(pid.strip()) for pid in profile_ids_str.split(",")]
        except ValueError:
            return Response(
                {"error": "profile_ids must be comma-separated integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use CostAggregatorService for parallel processing
        aggregator = CostAggregatorService()
        try:
            results = aggregator.calculate_multi_profile_costs(profile_ids, start_date, end_date)
            return Response({"results": results})
        finally:
            aggregator.shutdown()

    @action(detail=True, methods=["post"], url_path="progress")
    def create_progress(self, request: Request, pk: int) -> Response:
        """Create daily progress for a wall section under this profile."""
        profile = get_object_or_404(Profile, pk=pk)

        wall_section_id = request.data.get("wall_section_id")

        if not wall_section_id:
            return Response(
                {"wall_section_id": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate wall_section belongs to this profile
        wall_section = get_object_or_404(WallSection, pk=wall_section_id)
        if wall_section.profile_id != profile.id:
            return Response(
                {"wall_section_id": ["Wall section does not belong to this profile."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare data for serializer (use wall_section instead of wall_section_id)
        progress_data = {
            "wall_section": wall_section_id,
            "date": request.data.get("date"),
            "feet_built": request.data.get("feet_built"),
            "notes": request.data.get("notes", ""),
        }

        serializer = DailyProgressSerializer(data=progress_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
