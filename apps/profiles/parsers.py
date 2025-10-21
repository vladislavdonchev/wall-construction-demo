"""Config file parsers for wall construction profiles."""

from __future__ import annotations

from apps.profiles.constants import (
    MAX_HEIGHT,
    MAX_PROFILES,
    MAX_SECTIONS_PER_PROFILE,
    MAX_TOTAL_SECTIONS,
    MIN_HEIGHT,
)
from apps.profiles.services.simulator import ProfileConfig


class ConfigParser:
    """Parser for wall construction profile configuration files."""

    @staticmethod
    def _validate_heights(heights: list[int], line_num: int) -> None:
        """Validate section heights for a profile line.

        Args:
            heights: List of height values
            line_num: Line number for error messages

        Raises:
            ValueError: If heights are invalid
        """
        if not heights:
            msg = f"Line {line_num}: No heights specified. Each line must have at least one height value."
            raise ValueError(msg)

        for height in heights:
            if not MIN_HEIGHT <= height <= MAX_HEIGHT:
                msg = (
                    f"Line {line_num}: Height {height} is out of valid range. "
                    f"Heights must be between {MIN_HEIGHT} and {MAX_HEIGHT} feet. "
                    f"Example valid heights: 0, 15, 21, 30"
                )
                raise ValueError(msg)

        if len(heights) > MAX_SECTIONS_PER_PROFILE:
            msg = (
                f"Line {line_num}: Too many sections in this profile "
                f"(max {MAX_SECTIONS_PER_PROFILE}, got {len(heights)}). "
                f"Consider splitting into multiple profiles."
            )
            raise ValueError(msg)

    @staticmethod
    def _validate_profile_counts(profiles: list[ProfileConfig], total_sections: int) -> None:
        """Validate total profile and section counts.

        Args:
            profiles: List of parsed profiles
            total_sections: Total section count across all profiles

        Raises:
            ValueError: If counts exceed limits
        """
        if not profiles:
            msg = "No profiles found in configuration. Please provide at least one line with wall section heights. Example:\n21 25 28\n17\n17 22 17 19 17"
            raise ValueError(msg)

        if len(profiles) > MAX_PROFILES:
            msg = f"Too many profiles (max {MAX_PROFILES}, got {len(profiles)}). Please reduce the number of profile lines."
            raise ValueError(msg)

        if total_sections > MAX_TOTAL_SECTIONS:
            msg = (
                f"Too many total sections across all profiles "
                f"(max {MAX_TOTAL_SECTIONS}, got {total_sections}). "
                f"Please reduce the total number of wall sections."
            )
            raise ValueError(msg)

    @staticmethod
    def parse_config(config_text: str) -> list[ProfileConfig]:
        """Parse wall profile configuration.

        Format: Each line represents a profile with space-separated initial heights.
        Example:
            21 25 28
            17
            17 22 17 19 17

        Args:
            config_text: Configuration text with profiles

        Returns:
            List of profile configurations with section heights

        Raises:
            ValueError: If config format is invalid or heights out of range
        """
        profiles: list[ProfileConfig] = []
        lines = config_text.strip().split("\n")
        total_sections = 0

        for line_num, raw_line in enumerate(lines, 1):
            line_text = raw_line.strip()
            if not line_text:
                continue

            try:
                heights = [int(h) for h in line_text.split()]
            except ValueError as e:
                msg = f"Line {line_num}: Invalid number format. Each line must contain space-separated integers. Example: '21 25 28'"
                raise ValueError(msg) from e

            ConfigParser._validate_heights(heights, line_num)

            total_sections += len(heights)
            profiles.append(ProfileConfig(heights=heights))

        ConfigParser._validate_profile_counts(profiles, total_sections)

        return profiles
