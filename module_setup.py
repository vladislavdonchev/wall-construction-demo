#!/usr/bin/env python3
"""Module setup script for demo project."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


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
            print(f"Installing Python {version} via uv...")
            subprocess.run(["uv", "python", "install", version], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Installing Python {version} via uv...")
        subprocess.run(["uv", "python", "install", version], check=True)


def sync_dependencies(module_root: Path) -> None:
    """Sync pyproject.toml dependencies with uv."""
    print("Syncing dependencies with uv (including dev)...")
    subprocess.run(
        ["uv", "sync", "--dev"],
        cwd=module_root,
        check=True,
    )


def main() -> int:
    """Setup demo project venv and dependencies."""
    module_root = Path(__file__).parent.resolve()
    python_ver_file = module_root / "python.ver"

    if not python_ver_file.exists():
        print(f"Error: {python_ver_file} not found")
        return 1

    required_version = python_ver_file.read_text().strip()
    print(f"Setting up demo project with Python {required_version}...")

    try:
        check_uv()
        ensure_python_version(required_version)

        pyproject = module_root / "pyproject.toml"
        if not pyproject.exists():
            print(f"Error: {pyproject} not found")
            return 1

        sync_dependencies(module_root)

        print("\n✓ Setup complete for demo project")
        venv_dir = module_root / ".venv"
        print(f"  Activate: source {venv_dir}/bin/activate")
        print(f"  Run demo: ./scripts/ami-run.sh {module_root}/main.py")
        return 0

    except (subprocess.CalledProcessError, RuntimeError) as e:
        print(f"\n✗ Setup failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
