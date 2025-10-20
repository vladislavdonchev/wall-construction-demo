#!/usr/bin/env python3
"""Minimal test runner for demo project - no base dependencies."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run pytest using demo's .venv."""
    demo_root = Path(__file__).resolve().parent.parent
    venv_python = demo_root / ".venv" / "bin" / "python"

    if not venv_python.exists():
        sys.stderr.write(f"Error: {venv_python} not found. Run module_setup.py first.\n")
        return 1

    tests_dir = demo_root / "tests"
    if not tests_dir.exists():
        sys.stderr.write(f"No tests directory found at {tests_dir}. Nothing to test.\n")
        return 0

    # Build pytest command with default args if none provided
    cmd = [str(venv_python), "-m", "pytest"]

    # Add default args only if no args provided
    if len(sys.argv) == 1:
        cmd.extend(
            [
                "tests/",
                "-v",
                "--cov=apps",
                "--cov-report=term-missing",
            ]
        )
    else:
        cmd.extend(sys.argv[1:])

    try:
        subprocess.run(cmd, cwd=str(demo_root), check=True)
        return 0
    except subprocess.CalledProcessError as exc:
        return exc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
