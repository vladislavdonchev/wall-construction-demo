#!/usr/bin/env python3
"""Test runner for demo project."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main() -> int:
    """Run pytest with all command line arguments passed through."""
    demo_root = Path(__file__).resolve().parent.parent
    tests_dir = demo_root / "tests"

    if not tests_dir.exists():
        logging.info(f"No tests directory found at {tests_dir}. Nothing to test.")
        return 0

    test_files = list(tests_dir.rglob("test_*.py")) + list(tests_dir.rglob("*_test.py"))
    if not test_files:
        logging.info("No test files found. Nothing to test.")
        return 0

    cmd = [sys.executable, "-m", "pytest"] + sys.argv[1:]
    try:
        subprocess.run(cmd, cwd=str(demo_root), check=True)
        return 0
    except subprocess.CalledProcessError as exc:
        return exc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
