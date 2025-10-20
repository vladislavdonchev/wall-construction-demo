# Wall Construction API - Technical Specification

## Problem Overview

The Great Wall of Westeros requires a tracking system for multi-profile wall construction operations. Each construction profile must track daily progress, ice material consumption, and associated costs.

### Business Rules

- **Ice Consumption**: 195 cubic yards per linear foot of wall
- **Ice Cost**: 1,900 Gold Dragons per cubic yard
- **Daily Cost Formula**: `feet_built × 195 yd³/ft × 1,900 GD/yd³ = daily_cost`

### Requirements

1. Track multiple construction profiles simultaneously
2. Record daily wall construction progress (feet built per day)
3. Calculate daily ice usage for each profile
4. Provide cost overview reports with date range filtering
5. Support multi-threaded computation for aggregations
6. Run in HuggingFace Docker Space (file-based, no external services)

## Technology Stack

### Core Framework
- **Django 5.2.7 LTS** (released April 2, 2025)
  - Python 3.10-3.14 support
  - SQLite database (file-based persistence)
  - Built-in ORM with transaction support

- **Django REST Framework 3.16** (released March 28, 2025)
  - ViewSets for CRUD operations
  - Serializers for data validation
  - Pagination and filtering support

### Multi-Threading
- **Python concurrent.futures.ThreadPoolExecutor**
  - No external broker dependencies (Celery-free)
  - Configurable worker pool size
  - Suitable for CPU-bound aggregations

### Deployment
- **HuggingFace Docker Space Compatible**
  - SQLite database file (`db.sqlite3`)
  - No PostgreSQL, Redis, or RabbitMQ required
  - Single container deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     REST API Layer (DRF)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Profile     │  │  Progress    │  │  Analytics   │     │
│  │  ViewSet     │  │  ViewSet     │  │  ViewSet     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Profile     │  │  Ice Usage   │  │  Cost        │     │
│  │  Service     │  │  Calculator  │  │  Aggregator  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Profile     │  │  Wall        │  │  Daily       │     │
│  │  Repository  │  │  Section     │  │  Progress    │     │
│  │              │  │  Repository  │  │  Repository  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│               Django ORM + SQLite Database                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Profile     │  │  WallSection │  │  Daily       │     │
│  │  Model       │  │  Model       │  │  Progress    │     │
│  │              │  │              │  │  Model       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### ThreadPoolExecutor Integration

```python
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings

# services/cost_aggregator.py
class CostAggregator:
    def __init__(self):
        self.executor = ThreadPoolExecutor(
            max_workers=settings.WORKER_POOL_SIZE
        )

    def calculate_parallel_costs(self, profiles, date_range):
        futures = [
            self.executor.submit(self._calculate_cost, profile, date_range)
            for profile in profiles
        ]
        return [f.result() for f in futures]
```

## Data Models

### Profile Model
```python
from django.db import models

class Profile(models.Model):
    """Construction profile for wall building operations."""
    name = models.CharField(max_length=255, unique=True)
    team_lead = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'profiles'
        ordering = ['-created_at']
```

### WallSection Model
```python
class WallSection(models.Model):
    """Physical wall section assigned to a profile."""
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='wall_sections'
    )
    section_name = models.CharField(max_length=255)
    start_position = models.DecimalField(max_digits=10, decimal_places=2)
    target_length_feet = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wall_sections'
        unique_together = [['profile', 'section_name']]
```

### DailyProgress Model
```python
class DailyProgress(models.Model):
    """Daily construction progress for a wall section."""
    wall_section = models.ForeignKey(
        WallSection,
        on_delete=models.CASCADE,
        related_name='daily_progress'
    )
    date = models.DateField()
    feet_built = models.DecimalField(max_digits=10, decimal_places=2)
    ice_cubic_yards = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="195 cubic yards per foot"
    )
    cost_gold_dragons = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="1900 Gold Dragons per cubic yard"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'daily_progress'
        unique_together = [['wall_section', 'date']]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['wall_section', 'date']),
        ]
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### 1. List Profiles
```http
GET /api/profiles/
```

**Response**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Northern Watch",
      "team_lead": "Jon Snow",
      "is_active": true,
      "created_at": "2025-10-01T08:00:00Z"
    }
  ]
}
```

### 2. Create Profile
```http
POST /api/profiles/
Content-Type: application/json

{
  "name": "Eastern Defense",
  "team_lead": "Tormund Giantsbane",
  "is_active": true
}
```

### 3. Record Daily Progress
```http
POST /api/profiles/{profile_id}/progress/
Content-Type: application/json

{
  "wall_section_id": 5,
  "date": "2025-10-15",
  "feet_built": 12.5,
  "notes": "Clear weather, good progress"
}
```

**Response**
```json
{
  "id": 42,
  "wall_section_id": 5,
  "date": "2025-10-15",
  "feet_built": "12.50",
  "ice_cubic_yards": "2437.50",
  "cost_gold_dragons": "4631250.00",
  "notes": "Clear weather, good progress",
  "created_at": "2025-10-15T14:30:00Z"
}
```

**Calculation**
- Ice usage: 12.5 feet × 195 yd³/ft = 2,437.5 yd³
- Cost: 2,437.5 yd³ × 1,900 GD/yd³ = 4,631,250 GD

### 4. Daily Ice Usage by Profile
```http
GET /api/profiles/{profile_id}/daily-ice-usage/?date=2025-10-15
```

**Response**
```json
{
  "profile_id": 1,
  "profile_name": "Northern Watch",
  "date": "2025-10-15",
  "total_feet_built": "28.75",
  "total_ice_cubic_yards": "5606.25",
  "sections": [
    {
      "section_name": "Tower 1-2",
      "feet_built": "12.50",
      "ice_cubic_yards": "2437.50"
    },
    {
      "section_name": "Tower 2-3",
      "feet_built": "16.25",
      "ice_cubic_yards": "3168.75"
    }
  ]
}
```

### 5. Cost Overview with Date Range
```http
GET /api/profiles/{profile_id}/cost-overview/?start_date=2025-10-01&end_date=2025-10-15
```

**Response**
```json
{
  "profile_id": 1,
  "profile_name": "Northern Watch",
  "date_range": {
    "start": "2025-10-01",
    "end": "2025-10-15"
  },
  "summary": {
    "total_days": 15,
    "total_feet_built": "425.50",
    "total_ice_cubic_yards": "82972.50",
    "total_cost_gold_dragons": "157647750.00",
    "average_feet_per_day": "28.37",
    "average_cost_per_day": "10509850.00"
  },
  "daily_breakdown": [
    {
      "date": "2025-10-15",
      "feet_built": "28.75",
      "ice_cubic_yards": "5606.25",
      "cost_gold_dragons": "10651875.00"
    },
    {
      "date": "2025-10-14",
      "feet_built": "31.00",
      "ice_cubic_yards": "6045.00",
      "cost_gold_dragons": "11485500.00"
    }
  ]
}
```

## Multi-Threading Implementation

### Cost Aggregation Service

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.db.models import Sum

class CostAggregatorService:
    """
    Service for parallel cost calculations across multiple profiles.
    Uses ThreadPoolExecutor for CPU-bound aggregation tasks.
    """

    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or settings.WORKER_POOL_SIZE
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def calculate_multi_profile_costs(
        self,
        profile_ids: list[int],
        start_date: str,
        end_date: str
    ) -> list[dict]:
        """
        Calculate costs for multiple profiles in parallel.

        Args:
            profile_ids: List of profile IDs to process
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of cost summaries per profile
        """
        futures = {
            self.executor.submit(
                self._calculate_profile_cost,
                profile_id,
                start_date,
                end_date
            ): profile_id
            for profile_id in profile_ids
        }

        results = []
        for future in as_completed(futures):
            profile_id = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                # Log error and continue with other profiles
                logger.error(
                    f"Profile {profile_id} cost calculation failed: {exc}"
                )
                results.append({
                    "profile_id": profile_id,
                    "error": str(exc)
                })

        return results

    def _calculate_profile_cost(
        self,
        profile_id: int,
        start_date: str,
        end_date: str
    ) -> dict:
        """Calculate cost summary for a single profile."""
        from .repositories import DailyProgressRepository

        repo = DailyProgressRepository()

        # Use Django ORM aggregation for efficient DB queries
        aggregates = repo.get_aggregates_by_profile(
            profile_id,
            start_date,
            end_date
        )

        return {
            "profile_id": profile_id,
            "total_feet_built": str(aggregates["total_feet"]),
            "total_ice_cubic_yards": str(aggregates["total_ice"]),
            "total_cost_gold_dragons": str(aggregates["total_cost"]),
            "calculation_thread": threading.current_thread().name
        }

    def shutdown(self):
        """Gracefully shutdown the thread pool."""
        self.executor.shutdown(wait=True)
```

### Configuration

```python
# settings.py
WORKER_POOL_SIZE = 4  # Configurable based on container resources
```

### Usage in ViewSet

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class ProfileViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['get'])
    def bulk_cost_overview(self, request):
        """Calculate costs for multiple profiles in parallel."""
        profile_ids = request.query_params.getlist('profile_ids[]')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        aggregator = CostAggregatorService()
        try:
            results = aggregator.calculate_multi_profile_costs(
                profile_ids,
                start_date,
                end_date
            )
            return Response({"results": results})
        finally:
            aggregator.shutdown()
```

## Service Layer Design

### IceUsageCalculator

```python
from decimal import Decimal

class IceUsageCalculator:
    """Business logic for ice usage calculations."""

    ICE_PER_FOOT = Decimal("195")  # cubic yards per foot
    COST_PER_CUBIC_YARD = Decimal("1900")  # Gold Dragons

    @classmethod
    def calculate_ice_usage(cls, feet_built: Decimal) -> Decimal:
        """Calculate ice usage in cubic yards."""
        return feet_built * cls.ICE_PER_FOOT

    @classmethod
    def calculate_cost(cls, ice_cubic_yards: Decimal) -> Decimal:
        """Calculate cost in Gold Dragons."""
        return ice_cubic_yards * cls.COST_PER_CUBIC_YARD

    @classmethod
    def calculate_full_cost(cls, feet_built: Decimal) -> tuple[Decimal, Decimal]:
        """Calculate both ice usage and cost."""
        ice = cls.calculate_ice_usage(feet_built)
        cost = cls.calculate_cost(ice)
        return ice, cost
```

## Repository Layer Design

### DailyProgressRepository

```python
from django.db.models import Sum, Avg, Count
from decimal import Decimal

class DailyProgressRepository:
    """Data access layer for DailyProgress model."""

    def get_by_date(self, profile_id: int, date: str):
        """Retrieve all progress records for a profile on a specific date."""
        return DailyProgress.objects.filter(
            wall_section__profile_id=profile_id,
            date=date
        ).select_related('wall_section')

    def get_aggregates_by_profile(
        self,
        profile_id: int,
        start_date: str,
        end_date: str
    ) -> dict:
        """Get aggregated statistics for a profile within date range."""
        result = DailyProgress.objects.filter(
            wall_section__profile_id=profile_id,
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(
            total_feet=Sum('feet_built'),
            total_ice=Sum('ice_cubic_yards'),
            total_cost=Sum('cost_gold_dragons'),
            avg_feet=Avg('feet_built'),
            record_count=Count('id')
        )

        # Handle None values for empty querysets
        return {
            "total_feet": result["total_feet"] or Decimal("0"),
            "total_ice": result["total_ice"] or Decimal("0"),
            "total_cost": result["total_cost"] or Decimal("0"),
            "avg_feet": result["avg_feet"] or Decimal("0"),
            "record_count": result["record_count"]
        }
```

## HuggingFace Space Deployment

### Requirements

```python
# requirements.txt
Django==5.2.7
djangorestframework==3.16.0
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations and start server
CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:7860
```

### Space Configuration

```yaml
# README.md (HuggingFace Space header)
---
title: Wall Construction API
emoji: 🏰
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
---
```

### Database Persistence

- SQLite database file: `db.sqlite3`
- Persisted in HuggingFace Space persistent storage
- Automatic migrations on container startup
- No external database service required

## Error Handling

### Standard Error Response

```json
{
  "error": "validation_error",
  "message": "Invalid date format",
  "details": {
    "date": ["Date must be in YYYY-MM-DD format"]
  }
}
```

### HTTP Status Codes

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Testing Strategy

### Unit Tests
- Service layer: IceUsageCalculator calculations
- Repository layer: Query correctness
- Model layer: Validation rules

### Integration Tests
- API endpoints with test database
- ThreadPoolExecutor parallel execution
- Full request/response cycle

### Test Data
- Sample profiles with known outputs
- Edge cases: zero feet built, large numbers
- Date range boundaries

## Performance Considerations

### Database Optimization
- Indexes on `date` and `wall_section_id` fields
- `select_related()` for FK queries
- `aggregate()` for sum/avg calculations
- Database connection pooling (built into Django)

### Thread Pool Sizing
- Default: 4 workers
- Configurable via `WORKER_POOL_SIZE` setting
- Balance between parallelism and resource usage
- HuggingFace Space constraints: 2-4 workers recommended

### Query Optimization
```python
# Good: Single query with aggregation
DailyProgress.objects.filter(...).aggregate(Sum('cost_gold_dragons'))

# Bad: Multiple queries in loop
for progress in DailyProgress.objects.filter(...):
    total += progress.cost_gold_dragons
```

## Future Enhancements

1. **Caching Layer**: Redis cache for frequently accessed aggregations
2. **Async Views**: Upgrade to Django 5.x async views when DRF adds native support
3. **Background Tasks**: True Celery integration for long-running reports
4. **PostgreSQL**: Upgrade to PostgreSQL for production deployments
5. **Metrics Dashboard**: Real-time construction progress visualization
6. **Export Features**: CSV/PDF report generation
7. **Authentication**: Token-based API authentication
8. **Rate Limiting**: Throttling for cost-intensive aggregations

## Appendix: Constants

```python
# constants.py
from decimal import Decimal

# Wall Construction Constants
ICE_CUBIC_YARDS_PER_FOOT = Decimal("195")
GOLD_DRAGONS_PER_CUBIC_YARD = Decimal("1900")

# Calculated Constants
GOLD_DRAGONS_PER_FOOT = (
    ICE_CUBIC_YARDS_PER_FOOT * GOLD_DRAGONS_PER_CUBIC_YARD
)  # 370,500 GD per foot
```
