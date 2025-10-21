"""Profile models for Wall Construction API."""

from __future__ import annotations

from django.db import models


class Simulation(models.Model):
    """Simulation run record tracking input parameters and results."""

    config_text = models.TextField(help_text="Original wall config input")
    num_teams = models.IntegerField(help_text="Number of construction teams")
    start_date = models.DateField(help_text="Simulation start date")
    total_days = models.IntegerField(help_text="Total construction days")
    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total cost in Gold Dragons",
    )
    total_sections = models.IntegerField(help_text="Total number of wall sections")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "simulations"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of simulation."""
        return f"Simulation #{self.id} ({self.start_date}, {self.num_teams} teams)"


class Profile(models.Model):
    """Construction profile for wall building operations."""

    simulation = models.ForeignKey(
        Simulation,
        on_delete=models.CASCADE,
        related_name="profiles",
        help_text="Simulation this profile belongs to",
    )
    name = models.CharField(max_length=255)
    team_lead = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "profiles"
        ordering = ["-created_at"]
        unique_together = [["simulation", "name"]]

    def __str__(self) -> str:
        """Return string representation of profile."""
        return f"{self.name} (led by {self.team_lead})"


class WallSection(models.Model):
    """Physical wall section assigned to a profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="wall_sections",
    )
    section_name = models.CharField(max_length=255)
    initial_height = models.IntegerField(
        null=True,
        blank=True,
        help_text="Initial height in feet (0-30) for simulation",
    )
    current_height = models.IntegerField(
        null=True,
        blank=True,
        help_text="Current height in feet during simulation",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wall_sections"
        unique_together = [["profile", "section_name"]]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of wall section."""
        return f"{self.section_name} ({self.profile.name})"


class DailyProgress(models.Model):
    """Daily construction progress for a wall section."""

    wall_section = models.ForeignKey(
        WallSection,
        on_delete=models.CASCADE,
        related_name="daily_progress",
    )
    date = models.DateField()
    feet_built = models.DecimalField(max_digits=10, decimal_places=2)
    ice_cubic_yards = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="195 cubic yards per foot",
    )
    cost_gold_dragons = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="1900 Gold Dragons per cubic yard",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "daily_progress"
        unique_together = [["wall_section", "date"]]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["wall_section", "date"]),
        ]

    def __str__(self) -> str:
        """Return string representation of daily progress."""
        return f"{self.wall_section.section_name}: {self.feet_built} ft on {self.date}"
