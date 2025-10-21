# Wall Construction API - Technical Specification

## Problem Overview

The Great Wall of Westeros requires a simulation system for multi-profile wall construction operations. The system must parse configuration files specifying wall sections with varying heights, simulate concurrent team construction, and track daily progress with ice consumption and cost metrics.

### Business Rules

- **Ice Consumption**: 195 cubic yards per linear foot of wall
- **Ice Cost**: 1,900 Gold Dragons per cubic yard
- **Daily Cost Formula**: `feet_built × 195 yd³/ft × 1,900 GD/yd³ = daily_cost`
- **Target Height**: All sections must reach 30 feet
- **Daily Build Rate**: 1 foot per team per day
- **Team Assignment**: Round-robin across active sections

### Requirements

1. Parse multi-profile configuration (heights per section per profile)
2. Simulate concurrent wall construction with configurable team count
3. Track daily progress with automatic ice/cost calculations
4. Generate team activity logs to file system
5. Provide simulation overview endpoints
6. Run in HuggingFace Docker Space (file-based, no external services)

## Technology Stack

### Core Framework
- **Django 5.2.7** (Python 3.12.3)
  - SQLite database (file-based persistence)
  - Built-in ORM with transaction support
  - Migration system

- **Django REST Framework 3.16**
  - ViewSets for CRUD and custom actions
  - Serializers for data validation
  - Pagination support

### Multi-Threading
- **Python concurrent.futures.ThreadPoolExecutor**
  - Parallel wall section processing during simulation
  - No external broker dependencies
  - Configurable worker pool (default: 10 workers)

### Deployment
- **HuggingFace Docker Space Compatible**
  - SQLite database file (`db.sqlite3`)
  - File-based team logs (`logs/team_*.log`)
  - No PostgreSQL, Redis, or RabbitMQ required
  - Single container deployment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     REST API Layer (DRF)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Profile     │  │  WallSection │  │  Daily       │     │
│  │  ViewSet     │  │  ViewSet     │  │  Progress    │     │
│  │  + simulate  │  │  (CRUD)      │  │  ViewSet     │     │
│  │  + overview  │  │              │  │  (CRUD)      │     │
│  └──────┬───────┘  └──────────────┘  └──────────────┘     │
└─────────┼──────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Simulation Engine                          │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Config      │  │  Wall        │                        │
│  │  Parser      │  │  Simulator   │                        │
│  │              │  │ +ThreadPool  │                        │
│  └──────────────┘  └──────┬───────┘                        │
└──────────────────────────┼──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Django ORM + SQLite Database                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Profile     │  │  WallSection │  │  Daily       │     │
│  │              │──│              │──│  Progress    │     │
│  │  - name      │  │  - profile   │  │  - section   │     │
│  │  - lead      │  │  - name      │  │  - date      │     │
│  │  - active    │  │  - initial_h │  │  - feet      │     │
│  │              │  │  - current_h │  │  - ice       │     │
│  │              │  │              │  │  - cost      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Data Models

### Profile Model
```python
class Profile(models.Model):
    """Construction profile for wall building operations."""
    name = models.CharField(max_length=255, unique=True)
    team_lead = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    initial_height = models.IntegerField(
        null=True,
        blank=True,
        help_text="Initial height in feet (0-30) for simulation"
    )
    current_height = models.IntegerField(
        null=True,
        blank=True,
        help_text="Current height in feet during simulation"
    )
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

## Configuration Format

### Multi-Profile Config
```
21 25 28
17
17 22 17 19 17
```

**Rules:**
- Each line = 1 profile
- Space-separated integers = wall section heights (0-30 feet)
- Max 2000 sections per profile
- Empty lines ignored
- Whitespace trimmed

### Example
```
5 10 15
```
Creates:
- 1 profile ("Profile 1", "Team Lead 1")
- 3 wall sections at heights 5ft, 10ft, 15ft
- Each must reach 30ft

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### 1. Run Simulation
```http
POST /api/profiles/simulate/
Content-Type: application/json

{
  "config": "21 25 28\n17\n17 22 17 19 17",
  "num_teams": 10,
  "start_date": "2025-10-20"
}
```

**Response (201 Created)**
```json
{
  "total_profiles": 3,
  "total_sections": 9,
  "total_days": 15,
  "total_ice_cubic_yards": "82875.00",
  "total_cost_gold_dragons": "157462500.00"
}
```

**Validation:**
- `config`: Required, non-empty string
- `num_teams`: Optional integer (default: 10)
- `start_date`: Optional YYYY-MM-DD (default: today)

### 2. Daily Ice Usage
```http
GET /api/profiles/{profile_id}/days/{day}/
```

**Response**
```json
{
  "day": 3,
  "total_feet_built": "10.00",
  "total_ice_cubic_yards": "1950.00",
  "sections": [
    {
      "section_name": "Section 1",
      "feet_built": "1.00",
      "ice_cubic_yards": "195.00"
    }
  ]
}
```

### 3. Overview by Day (Single Profile)
```http
GET /api/profiles/{profile_id}/overview/{day}/
```

**Response**
```json
{
  "day": 5,
  "cost": "92625000.00"
}
```

### 4. Overview by Day (All Profiles)
```http
GET /api/profiles/overview/{day}/
```

**Response**
```json
{
  "day": 10,
  "cost": "157462500.00"
}
```

### 5. Total Overview
```http
GET /api/profiles/overview/
```

**Response**
```json
{
  "day": null,
  "cost": "157462500.00"
}
```

### CRUD Endpoints

**Profiles**
- `GET /api/profiles/` - List all
- `POST /api/profiles/` - Create
- `GET /api/profiles/{id}/` - Retrieve
- `PUT /api/profiles/{id}/` - Update
- `PATCH /api/profiles/{id}/` - Partial update
- `DELETE /api/profiles/{id}/` - Delete

**WallSections**
- `GET /api/wallsections/` - List all
- `POST /api/wallsections/` - Create
- `GET /api/wallsections/{id}/` - Retrieve
- `PUT /api/wallsections/{id}/` - Update
- `DELETE /api/wallsections/{id}/` - Delete
- Query param: `?profile={id}` - Filter by profile

**DailyProgress**
- `GET /api/progress/` - List all
- `POST /api/progress/` - Create (auto-calculates ice/cost)
- `GET /api/progress/{id}/` - Retrieve
- `PUT /api/progress/{id}/` - Update
- `DELETE /api/progress/{id}/` - Delete

## Simulation Engine

### ConfigParser

```python
@dataclass
class ProfileConfig:
    """Configuration for a single profile's wall sections."""
    profile_num: int
    heights: list[int]

class ConfigParser:
    """Parse multi-profile wall construction configuration."""

    MAX_HEIGHT = 30
    MAX_SECTIONS_PER_PROFILE = 2000

    @classmethod
    def parse(cls, config_text: str) -> list[ProfileConfig]:
        """Parse config string into ProfileConfig objects."""
        profiles: list[ProfileConfig] = []
        lines = config_text.strip().split("\n")

        for line_num, raw_line in enumerate(lines, 1):
            line_text = raw_line.strip()
            if not line_text:
                continue  # Skip empty lines

            try:
                heights = [int(h) for h in line_text.split()]
            except ValueError as e:
                raise ValueError(f"Line {line_num}: Invalid number format") from e

            for height in heights:
                if not 0 <= height <= cls.MAX_HEIGHT:
                    raise ValueError(
                        f"Line {line_num}: Height {height} out of range"
                    )

            if len(heights) > cls.MAX_SECTIONS_PER_PROFILE:
                raise ValueError(
                    f"Line {line_num}: Too many sections (max {cls.MAX_SECTIONS_PER_PROFILE})"
                )

            profiles.append(ProfileConfig(profile_num=line_num, heights=heights))

        if not profiles:
            raise ValueError("Config must contain at least one profile")

        return profiles
```

### WallSimulator

```python
class WallSimulator:
    """Simulate wall construction with parallel processing."""

    TARGET_HEIGHT = 30
    FEET_PER_DAY = 1

    def __init__(self, num_teams: int = 10):
        self.num_teams = num_teams
        self.executor = ThreadPoolExecutor(max_workers=num_teams)

    def simulate(
        self,
        profiles_config: list[ProfileConfig],
        start_date: date
    ) -> SimulationSummary:
        """Run simulation from config."""

        # 1. Initialize profiles and sections in database
        section_data = self._initialize_profiles(profiles_config)

        # 2. Simulate day-by-day until all sections reach 30ft
        day = 1
        current_date = start_date

        while any(s.current_height < self.TARGET_HEIGHT for s in section_data):
            # 3. Assign work (round-robin up to num_teams)
            sections_to_process = self._assign_work(section_data)

            if not sections_to_process:
                break  # No more work to assign

            # 4. Process sections in parallel using ThreadPoolExecutor
            results = self._process_day(sections_to_process, day)

            # 5. Save progress to database
            self._save_progress(results, current_date)

            # 6. Update section heights
            self._update_heights(section_data, results)

            day += 1
            current_date += timedelta(days=1)

        # 7. Calculate totals
        return self._calculate_summary(section_data, day - 1)

    def _process_day(
        self,
        sections: list[SectionData],
        day: int
    ) -> list[ProcessingResult]:
        """Process sections in parallel."""
        futures = [
            self.executor.submit(self._process_section, section, day)
            for section in sections
        ]
        return [f.result() for f in futures]

    def _process_section(
        self,
        section: SectionData,
        day: int
    ) -> ProcessingResult:
        """Process single section (runs in thread)."""
        feet_built = self.FEET_PER_DAY
        remaining = self.TARGET_HEIGHT - section.current_height

        if feet_built > remaining:
            feet_built = remaining

        ice = Decimal(str(feet_built)) * ICE_PER_FOOT
        cost = ice * COST_PER_CUBIC_YARD

        # Write team log
        self._write_log(section.team_num, day, section.section_num, feet_built)

        return ProcessingResult(
            section_id=section.id,
            feet_built=Decimal(str(feet_built)),
            ice_cubic_yards=ice,
            cost_gold_dragons=cost
        )
```

## Multi-Threading Details

### ThreadPoolExecutor Usage

```python
# Initialization (in WallSimulator.__init__)
self.executor = ThreadPoolExecutor(max_workers=num_teams)

# Parallel section processing (in _process_day)
futures = [
    self.executor.submit(self._process_section, section, day)
    for section in sections_to_process
]
results = [f.result() for f in futures]
```

**Benefits:**
- Each wall section processed in separate thread
- Up to `num_teams` sections processed concurrently
- Simulates real concurrent construction
- No GIL contention (I/O-bound file writes)

### Log File Output

Team logs written to `logs/team_{N}.log`:
```
Team 1: working on Profile 1, Section 1, building 1.00ft
Team 1: working on Profile 1, Section 2, building 1.00ft
Team 1: Section 3 completed!
Team 1: relieved
```

## Database Calculations

### Auto-Calculated Fields (DailyProgressSerializer)

```python
def create(self, validated_data):
    """Auto-calculate ice and cost from feet_built."""
    feet_built = validated_data['feet_built']

    ice_cubic_yards = feet_built * ICE_PER_FOOT  # 195 yd³/ft
    cost_gold_dragons = ice_cubic_yards * COST_PER_CUBIC_YARD  # 1900 GD/yd³

    return DailyProgress.objects.create(
        **validated_data,
        ice_cubic_yards=ice_cubic_yards,
        cost_gold_dragons=cost_gold_dragons
    )
```

### Aggregations (Overview Endpoints)

```python
# Total cost across all progress records
daily_progress = DailyProgress.objects.all()
aggregates = daily_progress.aggregate(total_cost=Sum("cost_gold_dragons"))
total_cost = aggregates["total_cost"] or Decimal("0.00")
```

## Testing

### Test Coverage
- **73 tests** across unit/integration/edge cases
- **98.41% code coverage**
- **0 MyPy/Ruff errors**

### Test Categories

**Unit Tests:**
- Model validation and constraints
- ConfigParser edge cases
- WallSimulator logic
- Serializer auto-calculations

**Integration Tests:**
- Full simulation workflow
- API endpoint responses
- Database persistence
- CRUD operations

**Edge Cases:**
- Invalid date format handling
- Profile with no simulation data
- Empty database queries
- Config parsing errors

### Running Tests
```bash
./scripts/run_tests.py
```

## Deployment

### HuggingFace Space

**Dockerfile**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:7860
```

**Space Configuration (README.md)**
```yaml
---
title: Wall Construction API
emoji: 🏰
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
---
```

### Persistence
- **Database**: `db.sqlite3` (auto-created, migrations applied on startup)
- **Logs**: `logs/team_*.log` (created during simulation)
- **No external services**: Self-contained deployment

## Performance

### Database Optimization
- Indexes on `date` and `wall_section_id`
- `select_related()` for foreign key queries
- `aggregate()` for sum calculations
- Single atomic transactions per simulation

### Thread Pool Sizing
- Default: 10 workers (configurable via `num_teams` param)
- Each worker processes 1 section per day
- I/O-bound (file writes), minimal CPU contention
- Suitable for HuggingFace Space resource limits

## Constants

```python
# constants.py
from decimal import Decimal

TARGET_HEIGHT = 30  # feet
ICE_PER_FOOT = Decimal("195")  # cubic yards
COST_PER_CUBIC_YARD = Decimal("1900")  # Gold Dragons
```

## Example Workflow

```python
# 1. POST simulation config
POST /api/profiles/simulate/
{
  "config": "5 10 15",
  "num_teams": 10
}

# 2. Check total cost
GET /api/profiles/overview/
→ {"day": null, "cost": "16965000.00"}

# 3. Check day 5 progress
GET /api/profiles/overview/5/
→ {"day": 5, "cost": "9262500.00"}

# 4. List all profiles
GET /api/profiles/
→ [{"id": 1, "name": "Profile 1", "team_lead": "Team Lead 1"}]

# 5. View section details
GET /api/wallsections/?profile=1
→ [
    {"section_name": "Section 1", "initial_height": 5, "current_height": 30},
    {"section_name": "Section 2", "initial_height": 10, "current_height": 30},
    {"section_name": "Section 3", "initial_height": 15, "current_height": 30}
  ]
```
