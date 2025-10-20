"""Profile models for Wall Construction API."""

from __future__ import annotations

from django.db import models


class Profile(models.Model):
    """Construction profile for wall building operations."""

    name = models.CharField(max_length=255, unique=True)
    team_lead = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "profiles"
        ordering = ["-created_at"]

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
    start_position = models.DecimalField(max_digits=10, decimal_places=2)
    target_length_feet = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wall_sections"
        unique_together = [["profile", "section_name"]]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of wall section."""
        return f"{self.section_name} ({self.profile.name})"
