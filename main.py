#!/usr/bin/env python3
"""Minimal demo script for iris.ai module."""

from __future__ import annotations

from loguru import logger


def main() -> int:
    """Main entry point for demo."""
    logger.info("Iris.ai demo starting...")
    logger.info("Module initialized successfully")
    logger.info("Demo complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
