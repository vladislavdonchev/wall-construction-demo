# Iris.ai Demo

This is a minimal demo project for the iris.ai AMI module.

## Setup

From the orchestrator root:

```bash
# Run with ami-run wrapper
./scripts/ami-run.sh clients/iris.ai/demo/main.py
```

## Structure

- `main.py` - Minimal demo script showing module initialization
- `__init__.py` - Python package marker
- `module_setup.py` - Environment setup using uv package manager
- `pyproject.toml` - Project dependencies and tool configuration
- `pytest.ini` - Test configuration
- `python.ver` - Python version requirement (3.12)
- `.gitignore` - Git ignore patterns (.venv, uv.lock, build artifacts)
- `scripts/run_tests.py` - Test runner script
- `README.md` - This file

## Development

The project follows AMI orchestrator standards:

- Dependencies managed via `pyproject.toml`
- Code quality enforced via ruff and mypy (no lint bypasses)
- Tests use pytest with strict configuration
- Python execution via `ami-run.sh` wrapper
