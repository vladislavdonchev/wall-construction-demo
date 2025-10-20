#!/usr/bin/env python3
"""Module setup script for demo project."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")


def check_uv() -> None:
    """Check if uv is installed and accessible."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        msg = "uv is not installed or not on PATH. Install: https://docs.astral.sh/uv/"
        raise RuntimeError(msg) from e


def ensure_python_version(version: str) -> None:
    """Ensure Python version is available via uv."""
    try:
        result = subprocess.run(
            ["uv", "python", "find", version],
            capture_output=True,
            text=True,
            check=True,
        )
        if not result.stdout.strip():
            logging.info(f"Installing Python {version} via uv...")
            subprocess.run(["uv", "python", "install", version], check=True)
    except subprocess.CalledProcessError:
        logging.info(f"Installing Python {version} via uv...")
        subprocess.run(["uv", "python", "install", version], check=True)


def sync_dependencies(module_root: Path) -> None:
    """Sync pyproject.toml dependencies with uv."""
    logging.info("Syncing dependencies with uv (all extras)...")
    subprocess.run(
        ["uv", "sync", "--all-extras"],
        cwd=module_root,
        check=True,
    )


def main() -> int:
    """Setup demo project venv and dependencies."""
    module_root = Path(__file__).parent.resolve()
    python_ver_file = module_root / "python.ver"

    if not python_ver_file.exists():
        logging.error(f"Error: {python_ver_file} not found")
        return 1

    required_version = python_ver_file.read_text().strip()
    logging.info(f"Setting up demo project with Python {required_version}...")

    try:
        check_uv()
        ensure_python_version(required_version)

        pyproject = module_root / "pyproject.toml"
        if not pyproject.exists():
            logging.error(f"Error: {pyproject} not found")
            return 1

        sync_dependencies(module_root)

        logging.info("\n✓ Setup complete for demo project")
        venv_dir = module_root / ".venv"
        logging.info(f"  Activate: source {venv_dir}/bin/activate")
        logging.info(f"  Run demo: ./scripts/ami-run.sh {module_root}/main.py")
        return 0

    except (subprocess.CalledProcessError, RuntimeError) as e:
        logging.error(f"\n✗ Setup failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
