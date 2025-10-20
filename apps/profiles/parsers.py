"""Config file parsers for wall construction profiles."""

from __future__ import annotations

from apps.profiles.services.simulator import ProfileConfig


class ConfigParser:
    """Parser for wall construction profile configuration files."""

    MAX_HEIGHT = 30
    MAX_SECTIONS_PER_PROFILE = 2000

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

        for line_num, raw_line in enumerate(lines, 1):
            line_text = raw_line.strip()
            if not line_text:
                continue

            try:
                heights = [int(h) for h in line_text.split()]
            except ValueError as e:
                raise ValueError(f"Line {line_num}: Invalid number format") from e

            for height in heights:
                if not 0 <= height <= ConfigParser.MAX_HEIGHT:
                    raise ValueError(f"Line {line_num}: Height {height} out of range (0-{ConfigParser.MAX_HEIGHT})")

            if not heights:
                raise ValueError(f"Line {line_num}: No heights specified")

            if len(heights) > ConfigParser.MAX_SECTIONS_PER_PROFILE:
                raise ValueError(f"Line {line_num}: Too many sections (max {ConfigParser.MAX_SECTIONS_PER_PROFILE}, got {len(heights)})")

            profiles.append(ProfileConfig(heights=heights))

        if not profiles:
            raise ValueError("No profiles found in config")

        return profiles
