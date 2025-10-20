"""Wall construction simulation service with multi-threaded team pool."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from apps.profiles.models import DailyProgress, Profile, WallSection


class ProfileConfig(BaseModel):
    """Configuration for a single wall profile."""

    model_config = ConfigDict(frozen=False)

    heights: list[int]
    name: str = ""
    team_lead: str = ""


class SectionData(BaseModel):
    """In-memory state for a wall section during simulation."""

    model_config = ConfigDict(frozen=False)

    id: int
    profile_id: int
    profile_name: str
    section_name: str
    current_height: int


class ProcessingResult(BaseModel):
    """Result from processing a single section for one day."""

    section_id: int
    feet_built: Decimal
    ice: Decimal
    cost: Decimal


class SimulationSummary(BaseModel):
    """Summary statistics from completed simulation."""

    total_days: int
    total_sections: int
    total_ice_cubic_yards: str
    total_cost_gold_dragons: str


class WallSimulator:
    """Simulates wall construction with parallel team execution.

    Uses ThreadPoolExecutor for multi-threaded simulation while maintaining
    SQLite compatibility through main-thread-only database operations.
    """

    TARGET_HEIGHT = 30
    ICE_PER_FOOT = Decimal("195")
    COST_PER_CUBIC_YARD = Decimal("1900")

    def __init__(self, num_teams: int, log_dir: str = "logs"):
        """Initialize simulator with team pool.

        Args:
            num_teams: Number of parallel teams (workers)
            log_dir: Directory for team log files
        """
        self.num_teams = num_teams
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        for team_id in range(num_teams):
            log_file = self.log_dir / f"team_{team_id}.log"
            log_file.write_text("")

    def simulate(
        self,
        profiles_config: list[ProfileConfig],
        start_date: date,
    ) -> SimulationSummary:
        """Run complete wall construction simulation.

        Args:
            profiles_config: List of profile configs with name and heights
            start_date: Simulation start date

        Returns:
            Summary statistics (total days, sections, ice, cost)
        """
        section_data = self._initialize_profiles(profiles_config)

        current_date = start_date
        day = 1

        while any(s.current_height < self.TARGET_HEIGHT for s in section_data):
            sections_to_process = self._assign_work(section_data)

            if not sections_to_process:
                break

            results = self._process_day(sections_to_process, day)

            self._save_results(results, current_date)

            self._update_state(section_data, results)

            current_date += timedelta(days=1)
            day += 1

        self._log_relief()

        total_ice = sum(DailyProgress.objects.all().values_list("ice_cubic_yards", flat=True))
        total_cost = sum(DailyProgress.objects.all().values_list("cost_gold_dragons", flat=True))

        return SimulationSummary(
            total_days=day - 1,
            total_sections=len(section_data),
            total_ice_cubic_yards=str(total_ice),
            total_cost_gold_dragons=str(total_cost),
        )

    def _initialize_profiles(
        self,
        profiles_config: list[ProfileConfig],
    ) -> list[SectionData]:
        """Initialize profiles and sections in database, return in-memory state.

        Args:
            profiles_config: List of profile configurations

        Returns:
            List of section data (plain dicts for thread-safe processing)
        """
        section_data: list[SectionData] = []

        for profile_num, config in enumerate(profiles_config, 1):
            if config.name:
                profile_name = config.name
            else:
                profile_name = f"Profile {profile_num}"

            if config.team_lead:
                team_lead = config.team_lead
            else:
                team_lead = f"Team Lead {profile_num}"

            heights = config.heights

            profile = Profile.objects.create(
                name=profile_name,
                team_lead=team_lead,
            )

            for section_num, height in enumerate(heights, 1):
                section = WallSection.objects.create(
                    profile=profile,
                    section_name=f"Section {section_num}",
                    start_position=Decimal(str(section_num - 1)),
                    target_length_feet=Decimal("1.0"),
                    initial_height=height,
                    current_height=height,
                )

                section_data.append(
                    SectionData(
                        id=section.id,
                        profile_id=profile.id,
                        profile_name=profile.name,
                        section_name=section.section_name,
                        current_height=height,
                    )
                )

        return section_data

    def _assign_work(
        self,
        section_data: list[SectionData],
    ) -> list[SectionData]:
        """Assign work to teams (limit by num_teams).

        Args:
            section_data: All sections with current state

        Returns:
            Sections assigned to teams for this day
        """
        incomplete_sections = [s for s in section_data if s.current_height < self.TARGET_HEIGHT]

        return incomplete_sections[: self.num_teams]

    def _process_day(
        self,
        sections: list[SectionData],
        day: int,
    ) -> list[ProcessingResult]:
        """Process one day of construction with parallel teams.

        Args:
            sections: Sections to process
            day: Current day number

        Returns:
            Results from all teams
        """
        with ThreadPoolExecutor(max_workers=self.num_teams) as executor:
            futures = {
                executor.submit(
                    self._process_section,
                    section,
                    day,
                    team_id,
                ): section
                for team_id, section in enumerate(sections)
            }

            results: list[ProcessingResult] = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        return results

    def _process_section(
        self,
        section: SectionData,
        day: int,
        team_id: int,
    ) -> ProcessingResult:
        """Process one section for one day (worker function - NO DB ACCESS).

        Args:
            section: Section data (plain dict)
            day: Current day number
            team_id: Team ID for logging

        Returns:
            Processing result
        """
        feet_built = 1
        ice = Decimal(str(feet_built)) * self.ICE_PER_FOOT
        cost = ice * self.COST_PER_CUBIC_YARD

        new_height = section.current_height + feet_built

        log_file = self.log_dir / f"team_{team_id}.log"
        with log_file.open("a") as f:
            if new_height >= self.TARGET_HEIGHT:
                f.write(f"Day {day}: Team {team_id} completed {section.section_name} ({section.profile_name})\n")
            else:
                f.write(f"Day {day}: Team {team_id} worked on {section.section_name} ({section.profile_name}) - {new_height}/30 ft\n")

        return ProcessingResult(
            section_id=section.id,
            feet_built=Decimal(str(feet_built)),
            ice=ice,
            cost=cost,
        )

    def _save_results(
        self,
        results: list[ProcessingResult],
        current_date: date,
    ) -> None:
        """Save day results to database (MAIN THREAD ONLY).

        Args:
            results: Processing results from all teams
            current_date: Current simulation date
        """
        progress_records = [
            DailyProgress(
                wall_section_id=r.section_id,
                date=current_date,
                feet_built=r.feet_built,
                ice_cubic_yards=r.ice,
                cost_gold_dragons=r.cost,
                notes="Simulated construction",
            )
            for r in results
        ]

        DailyProgress.objects.bulk_create(progress_records)

    def _update_state(
        self,
        section_data: list[SectionData],
        results: list[ProcessingResult],
    ) -> None:
        """Update in-memory section state after day completion.

        Args:
            section_data: All sections
            results: Day results
        """
        for result in results:
            matching_sections = [s for s in section_data if s.id == result.section_id]
            if not matching_sections:
                msg = f"Section {result.section_id} not found in section_data"
                raise ValueError(msg)
            section = matching_sections[0]
            section.current_height += 1

            WallSection.objects.filter(id=section.id).update(current_height=section.current_height)

    def _log_relief(self) -> None:
        """Log team relief when simulation complete."""
        for team_id in range(self.num_teams):
            log_file = self.log_dir / f"team_{team_id}.log"
            with log_file.open("a") as f:
                f.write(f"Team {team_id}: relieved\n")
