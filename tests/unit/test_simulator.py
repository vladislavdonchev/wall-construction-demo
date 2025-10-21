"""Unit tests for wall construction simulator."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from apps.profiles.models import DailyProgress, Profile, Simulation, WallSection
from apps.profiles.services.simulator import ProfileConfig, SectionData, WallSimulator


@pytest.mark.django_db
class TestWallSimulator:
    """Test cases for WallSimulator."""

    def test_initialize_single_profile(self, simulation: Simulation, tmp_path: Path) -> None:
        """Test initializing simulator with single profile."""
        profiles_config = [ProfileConfig(heights=[21, 25, 28])]

        simulator = WallSimulator(num_teams=2, log_dir=str(tmp_path))
        section_data = simulator._initialize_profiles(profiles_config, simulation)

        assert len(section_data) == 3
        assert Profile.objects.filter(simulation=simulation).count() == 1
        assert WallSection.objects.count() == 3

        profile = Profile.objects.filter(simulation=simulation).first()
        assert profile is not None
        assert profile.name == "Profile 1"

    def test_initialize_multiple_profiles(self, simulation: Simulation, tmp_path: Path) -> None:
        """Test initializing simulator with multiple profiles."""
        profiles_config = [
            ProfileConfig(heights=[21, 25, 28]),
            ProfileConfig(heights=[17]),
            ProfileConfig(heights=[17, 22, 17, 19, 17]),
        ]

        simulator = WallSimulator(num_teams=4, log_dir=str(tmp_path))
        section_data = simulator._initialize_profiles(profiles_config, simulation)

        assert len(section_data) == 9
        assert Profile.objects.filter(simulation=simulation).count() == 3
        assert WallSection.objects.count() == 9

    def test_assign_work_limits_by_teams(self, tmp_path: Path) -> None:
        """Test that work assignment respects team limit."""
        section_data = [
            SectionData(
                id=i,
                profile_id=1,
                profile_name="Profile 1",
                section_name=f"Section {i}",
                current_height=20,
            )
            for i in range(10)
        ]

        simulator = WallSimulator(num_teams=3, log_dir=str(tmp_path))
        assigned = simulator._assign_work(section_data)

        assert len(assigned) == 3

    def test_assign_work_skips_completed_sections(self, tmp_path: Path) -> None:
        """Test that completed sections are not assigned."""
        section_data = [
            SectionData(id=1, profile_id=1, profile_name="Profile 1", section_name="Section 1", current_height=30),
            SectionData(id=2, profile_id=1, profile_name="Profile 1", section_name="Section 2", current_height=25),
            SectionData(id=3, profile_id=1, profile_name="Profile 1", section_name="Section 3", current_height=30),
            SectionData(id=4, profile_id=1, profile_name="Profile 1", section_name="Section 4", current_height=28),
        ]

        simulator = WallSimulator(num_teams=5, log_dir=str(tmp_path))
        assigned = simulator._assign_work(section_data)

        assert len(assigned) == 2
        assert all(s.current_height < 30 for s in assigned)

    def test_process_section_calculates_correctly(self, tmp_path: Path) -> None:
        """Test that section processing calculates ice and cost correctly."""
        section = SectionData(
            id=1,
            profile_id=1,
            profile_name="Profile 1",
            section_name="Section 1",
            current_height=20,
        )

        simulator = WallSimulator(num_teams=1, log_dir=str(tmp_path))
        result = simulator._process_section(section, day=1, team_id=0)

        assert result.section_id == 1
        assert result.feet_built == Decimal("1")
        assert result.ice == Decimal("195")
        assert result.cost == Decimal("370500")

    def test_process_section_writes_log(self, tmp_path: Path) -> None:
        """Test that section processing writes to log file."""
        section = SectionData(
            id=1,
            profile_id=1,
            profile_name="Profile 1",
            section_name="Section 1",
            current_height=20,
        )

        simulator = WallSimulator(num_teams=1, log_dir=str(tmp_path))
        simulator._process_section(section, day=1, team_id=0)

        log_file = tmp_path / "team_0.log"
        assert log_file.exists()

        log_content = log_file.read_text()
        assert "Day 1" in log_content
        assert "Section 1" in log_content

    def test_process_section_logs_completion(self, tmp_path: Path) -> None:
        """Test that section completion is logged."""
        section = SectionData(
            id=1,
            profile_id=1,
            profile_name="Profile 1",
            section_name="Section 1",
            current_height=29,
        )

        simulator = WallSimulator(num_teams=1, log_dir=str(tmp_path))
        simulator._process_section(section, day=1, team_id=0)

        log_file = tmp_path / "team_0.log"
        log_content = log_file.read_text()
        assert "completed" in log_content

    def test_simulate_simple_profile(self, simulation: Simulation, tmp_path: Path) -> None:
        """Test complete simulation with simple profile."""
        profiles_config = [ProfileConfig(heights=[28, 29])]

        simulator = WallSimulator(num_teams=2, log_dir=str(tmp_path))
        result = simulator.simulate(profiles_config, date(2025, 10, 20), simulation)

        assert result.total_days == 2
        assert result.total_sections == 2

        # 3 DailyProgress records: Day 1 both sections (28→29, 29→30), Day 2 first section only (29→30)
        assert DailyProgress.objects.count() == 3

        profile = Profile.objects.filter(simulation=simulation).first()
        assert profile is not None

        sections = WallSection.objects.filter(profile=profile)
        for section in sections:
            assert section.current_height == 30

    def test_simulate_creates_logs(self, simulation: Simulation, tmp_path: Path) -> None:
        """Test that simulation creates team log files."""
        profiles_config = [ProfileConfig(heights=[28])]

        simulator = WallSimulator(num_teams=2, log_dir=str(tmp_path))
        simulator.simulate(profiles_config, date(2025, 10, 20), simulation)

        assert (tmp_path / "team_0.log").exists()
        assert (tmp_path / "team_1.log").exists()

        log_content = (tmp_path / "team_0.log").read_text()
        assert "relieved" in log_content

    def test_simulate_respects_team_limit(self, simulation: Simulation, tmp_path: Path) -> None:
        """Test that simulation respects team limit."""
        profiles_config = [ProfileConfig(heights=[25, 25, 25, 25, 25])]

        simulator = WallSimulator(num_teams=2, log_dir=str(tmp_path))
        simulator.simulate(profiles_config, date(2025, 10, 20), simulation)

        progress_by_day: dict[str, int] = {}
        for progress in DailyProgress.objects.all():
            day_key = progress.date.isoformat()
            progress_by_day[day_key] = progress_by_day.get(day_key, 0) + 1

        for count in progress_by_day.values():
            assert count <= 2

    def test_simulate_with_varying_heights(self, simulation: Simulation, tmp_path: Path) -> None:
        """Test simulation with varying initial heights."""
        profiles_config = [ProfileConfig(heights=[21, 25, 28, 30, 17])]

        simulator = WallSimulator(num_teams=3, log_dir=str(tmp_path))
        result = simulator.simulate(profiles_config, date(2025, 10, 20), simulation)

        assert result.total_sections == 5

        sections_with_height_30 = WallSection.objects.filter(initial_height=30, current_height=30).count()
        assert sections_with_height_30 == 1

        all_sections = WallSection.objects.all()
        for section in all_sections:
            assert section.current_height == 30
