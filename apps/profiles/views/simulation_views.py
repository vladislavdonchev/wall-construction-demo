"""Mixin for wall construction simulation."""

from __future__ import annotations

import logging
from datetime import date, datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.profiles.constants import MAX_TEAMS, MIN_TEAMS
from apps.profiles.models import Profile
from apps.profiles.parsers import ConfigParser
from apps.profiles.services.simulator import WallSimulator

logger = logging.getLogger(__name__)


class SimulationMixin:
    """Mixin providing simulation endpoints."""

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
        # Log simulation request
        client_ip = request.META.get("REMOTE_ADDR", "unknown")
        logger.info(f"Simulation request from {client_ip}")

        config_text = request.data.get("config")
        num_teams = request.data.get("num_teams", 4)
        start_date_str = request.data.get("start_date")

        # Validate required parameters
        if not config_text:
            logger.warning(f"Missing config parameter from {client_ip}")
            raise serializers.ValidationError({"config": "config parameter is required"})

        # Validate and parse start_date
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError as e:
                logger.warning(f"Invalid start_date from {client_ip}: {start_date_str}")
                raise serializers.ValidationError({"start_date": "start_date must be in YYYY-MM-DD format"}) from e
        else:
            start_date = date.today()

        # Validate num_teams with resource limits
        try:
            num_teams = int(num_teams)
            if num_teams < MIN_TEAMS:
                msg = f"num_teams must be at least {MIN_TEAMS}"
                raise ValueError(msg)
            if num_teams > MAX_TEAMS:
                msg = f"num_teams must not exceed {MAX_TEAMS} (got {num_teams}). Please use fewer teams."
                raise ValueError(msg)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid num_teams from {client_ip}: {num_teams}")
            raise serializers.ValidationError({"num_teams": str(e)}) from e

        # Parse and validate configuration
        parser = ConfigParser()
        try:
            profiles_config = parser.parse_config(config_text)
        except ValueError as e:
            logger.warning(f"Invalid config from {client_ip}: {e}")
            raise serializers.ValidationError({"config": str(e)}) from e

        # Set profile names and team leads
        for i, profile_config in enumerate(profiles_config, 1):
            profile_config.name = f"Profile {i}"
            profile_config.team_lead = f"Team Lead {i}"

        # Run simulation in atomic transaction to prevent data loss on errors
        # Transaction automatically rolls back on any exception
        with transaction.atomic():
            # Clear previous simulation data to avoid unique constraint violations
            # This cascades to WallSection and DailyProgress due to ForeignKey constraints
            Profile.objects.all().delete()
            logger.info(f"Cleared previous simulation data for {client_ip}")

            # Run simulation
            simulator = WallSimulator(num_teams=num_teams)
            result = simulator.simulate(profiles_config, start_date)

            logger.info(
                f"Simulation completed successfully for {client_ip}: "
                f"{result.total_sections} sections, {result.total_days} days, "
                f"{result.total_cost_gold_dragons} GD"
            )

        return Response(result.model_dump(), status=201)
