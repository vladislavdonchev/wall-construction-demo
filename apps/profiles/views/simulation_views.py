"""Mixin for wall construction simulation."""

from __future__ import annotations

from datetime import date, datetime

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response

from apps.profiles.parsers import ConfigParser
from apps.profiles.services.simulator import WallSimulator


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
        config_text = request.data.get("config")
        num_teams = request.data.get("num_teams", 4)
        start_date_str = request.data.get("start_date")

        if not config_text:
            raise serializers.ValidationError({"config": "config parameter is required"})

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError as e:
                raise serializers.ValidationError({"start_date": "start_date must be in YYYY-MM-DD format"}) from e
        else:
            start_date = date.today()

        try:
            num_teams = int(num_teams)
            if num_teams < 1:
                raise ValueError("num_teams must be positive")
        except (ValueError, TypeError) as e:
            raise serializers.ValidationError({"num_teams": "num_teams must be a positive integer"}) from e

        parser = ConfigParser()
        try:
            profiles_config = parser.parse_config(config_text)
        except ValueError as e:
            raise serializers.ValidationError({"config": f"Invalid config format: {e}"}) from e

        for i, profile_config in enumerate(profiles_config, 1):
            profile_config.name = f"Profile {i}"
            profile_config.team_lead = f"Team Lead {i}"

        try:
            simulator = WallSimulator(num_teams=num_teams)
            result = simulator.simulate(profiles_config, start_date)
        except Exception as e:
            raise APIException(f"Simulation failed: {e}") from e

        return Response(result.model_dump(), status=201)
