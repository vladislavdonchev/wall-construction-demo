"""Unit tests for config parsers."""

from __future__ import annotations

import pytest

from apps.profiles.parsers import ConfigParser


class TestConfigParser:
    """Test cases for ConfigParser."""

    def test_parse_single_profile(self) -> None:
        """Test parsing single profile with multiple sections."""
        config_text = "21 25 28"
        parser = ConfigParser()
        result = parser.parse_config(config_text)

        assert len(result) == 1
        assert result[0].heights == [21, 25, 28]

    def test_parse_multiple_profiles(self) -> None:
        """Test parsing multiple profiles."""
        config_text = "21 25 28\n17\n17 22 17 19 17"
        parser = ConfigParser()
        result = parser.parse_config(config_text)

        assert len(result) == 3
        assert result[0].heights == [21, 25, 28]
        assert result[1].heights == [17]
        assert result[2].heights == [17, 22, 17, 19, 17]

    def test_parse_with_whitespace(self) -> None:
        """Test parsing with extra whitespace."""
        config_text = "  21  25  28  \n\n17\n  "
        parser = ConfigParser()
        result = parser.parse_config(config_text)

        assert len(result) == 2
        assert result[0].heights == [21, 25, 28]
        assert result[1].heights == [17]

    def test_parse_min_height(self) -> None:
        """Test parsing minimum valid height (0)."""
        config_text = "0 5 10"
        parser = ConfigParser()
        result = parser.parse_config(config_text)

        assert result[0].heights == [0, 5, 10]

    def test_parse_max_height(self) -> None:
        """Test parsing maximum valid height (30)."""
        config_text = "25 28 30"
        parser = ConfigParser()
        result = parser.parse_config(config_text)

        assert result[0].heights == [25, 28, 30]

    def test_parse_empty_config_fails(self) -> None:
        """Test that empty config raises ValueError."""
        config_text = ""
        parser = ConfigParser()

        with pytest.raises(ValueError, match="No profiles found"):
            parser.parse_config(config_text)

    def test_parse_whitespace_only_fails(self) -> None:
        """Test that whitespace-only config raises ValueError."""
        config_text = "   \n  \n  "
        parser = ConfigParser()

        with pytest.raises(ValueError, match="No profiles found"):
            parser.parse_config(config_text)

    def test_parse_invalid_number_fails(self) -> None:
        """Test that non-numeric values raise ValueError."""
        config_text = "21 abc 28"
        parser = ConfigParser()

        with pytest.raises(ValueError, match="Invalid number format"):
            parser.parse_config(config_text)

    def test_parse_negative_height_fails(self) -> None:
        """Test that negative height raises ValueError."""
        config_text = "21 -5 28"
        parser = ConfigParser()

        with pytest.raises(ValueError, match="out of valid range"):
            parser.parse_config(config_text)

    def test_parse_height_above_30_fails(self) -> None:
        """Test that height above 30 raises ValueError."""
        config_text = "21 35 28"
        parser = ConfigParser()

        with pytest.raises(ValueError, match="out of valid range"):
            parser.parse_config(config_text)

    def test_parse_too_many_sections_fails(self) -> None:
        """Test that more than 2000 sections raises ValueError."""
        heights = " ".join(str(i % 30) for i in range(2001))
        config_text = heights
        parser = ConfigParser()

        with pytest.raises(ValueError, match="Too many sections"):
            parser.parse_config(config_text)

    def test_parse_max_sections_succeeds(self) -> None:
        """Test that exactly 2000 sections is allowed."""
        heights = " ".join(str(i % 30) for i in range(2000))
        config_text = heights
        parser = ConfigParser()

        result = parser.parse_config(config_text)
        assert len(result) == 1
        assert len(result[0].heights) == 2000

    def test_parse_all_sections_at_target_height_fails(self) -> None:
        """Test that config with all sections at target height is rejected."""
        parser = ConfigParser()

        with pytest.raises(ValueError, match="already at target height"):
            parser.parse_config("30 30 30")

    def test_parse_some_sections_at_target_height_succeeds(self) -> None:
        """Test that config with some sections at target height is accepted."""
        parser = ConfigParser()

        result = parser.parse_config("29 30")
        assert len(result) == 1
        assert result[0].heights == [29, 30]

        result = parser.parse_config("0 30 30")
        assert len(result) == 1
        assert result[0].heights == [0, 30, 30]
