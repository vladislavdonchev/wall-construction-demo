---
title: Wall Construction API
emoji: 🏰
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
---

# Wall Construction Tracker

A full-stack application for tracking multi-profile wall construction operations, ice material consumption, and associated costs. Features a React GUI frontend and Django REST API backend.

## Features

- **Multi-Profile Tracking**: Manage multiple construction profiles simultaneously
- **Daily Progress Recording**: Track feet built, ice usage, and costs per day
- **Cost Aggregation**: Multi-threaded cost calculations using ThreadPoolExecutor
- **Date Range Analytics**: Get cost overviews and breakdowns for any date range
- **Auto-Calculation**: Automatically calculate ice usage (195 yd³/ft) and costs (1,900 GD/yd³)

## API Endpoints

### Profiles

- `GET /api/profiles/` - List all profiles
- `POST /api/profiles/` - Create new profile
- `GET /api/profiles/{id}/` - Get profile details
- `PUT /api/profiles/{id}/` - Update profile
- `DELETE /api/profiles/{id}/` - Delete profile

### Daily Progress

- `POST /api/profiles/{id}/progress/` - Record daily progress for a profile
- `GET /api/profiles/{id}/daily-ice-usage/?date=YYYY-MM-DD` - Get ice usage for a date
- `GET /api/profiles/{id}/cost-overview/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Get cost overview

### Bulk Operations

- `GET /api/profiles/bulk-cost-overview/?profile_ids=1,2,3&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Parallel cost calculation

### Wall Sections

- `GET /api/wallsections/` - List all wall sections
- `POST /api/wallsections/` - Create new wall section
- `GET /api/wallsections/?profile={id}` - Filter by profile

## Example Usage

### Create a Profile

```bash
curl -X POST http://localhost:7860/api/profiles/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Northern Watch",
    "team_lead": "Jon Snow",
    "is_active": true
  }'
```

### Record Daily Progress

```bash
curl -X POST http://localhost:7860/api/profiles/1/progress/ \
  -H "Content-Type: application/json" \
  -d '{
    "wall_section_id": 5,
    "date": "2025-10-15",
    "feet_built": 12.5,
    "notes": "Clear weather, good progress"
  }'
```

**Response:**
```json
{
  "id": 42,
  "wall_section": 5,
  "date": "2025-10-15",
  "feet_built": "12.50",
  "ice_cubic_yards": "2437.50",
  "cost_gold_dragons": "4631250.00",
  "notes": "Clear weather, good progress",
  "created_at": "2025-10-15T14:30:00Z"
}
```

### Get Cost Overview

```bash
curl "http://localhost:7860/api/profiles/1/cost-overview/?start_date=2025-10-01&end_date=2025-10-15"
```

## Local Development

### Setup

```bash
# Install dependencies using uv
uv sync

# Run migrations
uv run python manage.py migrate

# Start development server
uv run python manage.py runserver
```

### Run Tests

```bash
# Run all tests
uv run python -m pytest

# Run with coverage
uv run python -m pytest --cov=apps
```

### Code Quality

```bash
# Run ruff linter
uv run ruff check .

# Run mypy type checker
uv run mypy apps/
```

## HuggingFace Space Deployment

This project is configured for deployment to HuggingFace Spaces using Docker.

### Build and Test Locally

```bash
# Build Docker image
docker build -t wall-api .

# Run container
docker run -p 7860:7860 wall-api

# Test API
curl http://localhost:7860/api/profiles/
```

### Database Persistence

- Uses SQLite database (`db.sqlite3`)
- Database persists in HuggingFace Space storage
- Automatic migrations on container startup
- No external database service required

## Project Structure

- `apps/profiles/` - Profile, WallSection, and DailyProgress models and APIs
  - `models.py` - Django ORM models
  - `views.py` - DRF ViewSets
  - `serializers.py` - Data validation and serialization
  - `repositories.py` - Data access layer
  - `services/` - Business logic (calculators, aggregators)
- `config/` - Django settings and URL configuration
- `tests/` - Unit and integration tests
- `pyproject.toml` - Project dependencies (managed by uv)
- `Dockerfile` - HuggingFace Space deployment configuration
- `SPEC-DEMO.md` - Complete technical specification

## Technology Stack

### Backend
- **Django 5.2.7 LTS** - Web framework
- **Django REST Framework 3.16** - API framework
- **Python 3.12** - Programming language
- **Gunicorn** - WSGI HTTP server
- **uv** - Fast Python package manager
- **SQLite** - File-based database
- **ThreadPoolExecutor** - Parallel cost calculations
- **pytest** - Testing framework

### Frontend
- **React 18** - UI framework
- **Vite 6** - Build tool
- **Tailwind CSS 3** - Utility-first CSS
- **Recharts 2** - Chart library
- **Hash-based routing** - Client-side navigation

### Infrastructure
- **Nginx** - Reverse proxy and static file server
- **Supervisor** - Process control system
- **Docker multi-stage builds** - Optimized deployment

## Development Standards

- Dependencies managed via `pyproject.toml` (NOT requirements.txt)
- Code quality enforced via ruff and mypy (zero tolerance)
- 100% test-driven development with pytest
- Repository pattern for data access
- Service layer for business logic
- Explicit None handling (no implicit defaults)
- Fail-fast error handling (no exception suppression)
