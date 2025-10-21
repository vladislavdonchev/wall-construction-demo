"""ViewSet for Simulation model."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.profiles.models import Simulation
from apps.profiles.serializers import SimulationDetailSerializer, SimulationSerializer
from apps.profiles.services.queries import ReportingQueries


class SimulationViewSet(viewsets.ReadOnlyModelViewSet[Simulation]):
    """ViewSet for listing and retrieving simulations."""

    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer
    pagination_class = None  # Disable pagination - users will have few simulations

    def get_serializer_class(self) -> type[serializers.BaseSerializer[Any]]:
        """Return SimulationDetailSerializer for retrieve action."""
        if self.action == "retrieve":
            return SimulationDetailSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["get"], url_path="overview")
    def overview(self, request: Request, **kwargs: Any) -> Response:
        """Get overview totals for a specific simulation.

        Returns cost and days for the selected simulation.
        """
        # Perform permission checks using request
        self.check_permissions(request)

        # Store kwargs for use by get_object() (DRF requirement)
        self.kwargs = kwargs

        # Get simulation using pk from kwargs
        simulation = self.get_object()

        # Get cost and days for this simulation
        total_cost = ReportingQueries.get_cost_overview(simulation.id, None, None)
        total_days = ReportingQueries.get_total_days(simulation.id)

        return Response(
            {
                "day": total_days,
                "cost": str(total_cost),
            }
        )
