# Wall Construction Tracker - Software Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Deployment Architecture](#deployment-architecture)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [Data Model Design](#data-model-design)
6. [Simulation Engine](#simulation-engine)
7. [API Design](#api-design)
8. [Design Decisions & Rationale](#design-decisions--rationale)

---

## System Overview

The Wall Construction Tracker is a full-stack web application that simulates multi-profile wall construction operations, tracking daily progress, ice material consumption, and associated costs in Gold Dragons (GD).

### Key Capabilities
- Parse multi-profile wall configurations with varying section heights
- Simulate concurrent team construction with configurable team counts
- Track daily progress with automatic ice/cost calculations
- Generate team activity logs to filesystem
- Provide simulation overview and reporting endpoints
- Deploy as single Docker container with no external service dependencies

### Technology Stack Summary
- **Backend**: Django 5.2.7 + Django REST Framework 3.16 (Python 3.12)
- **Frontend**: React 18 + Vite 6 + Tailwind CSS 3
- **Database**: SQLite (file-based)
- **Web Server**: nginx (reverse proxy + static files)
- **Process Management**: Supervisor
- **Containerization**: Docker multi-stage builds

---

## Deployment Architecture

### Container Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Container (Port 7860)                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     nginx (Port 7860)                      │ │
│  │  - Reverse proxy to Django                                 │ │
│  │  - Serves React SPA                                        │ │
│  │  - Routes /api/* → Django backend                          │ │
│  │  - Routes /* → React frontend                              │ │
│  └──────────────┬────────────────────────┬────────────────────┘ │
│                 │                        │                       │
│  ┌──────────────▼──────────┐  ┌─────────▼────────────────────┐ │
│  │   Django + Gunicorn     │  │   React SPA (built dist/)    │ │
│  │   (Port 8000, internal) │  │   Single-page application    │ │
│  │   - REST API            │  │   - Hash-based routing       │ │
│  │   - Simulation engine   │  │   - Tailwind CSS             │ │
│  │   - SQLite database     │  │   - Recharts visualizations  │ │
│  └─────────────────────────┘  └──────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               Supervisor (Process Control)                 │ │
│  │  - Manages Django (Gunicorn) and nginx processes           │ │
│  │  - Automatic restarts on failure                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

### Multi-Stage Docker Build

**Stage 1: Frontend Builder**
```dockerfile
FROM node:22-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build  # → produces frontend/dist/
```

**Stage 2: Production Image**
```dockerfile
FROM nginx:alpine
# Install Python, supervisor, dependencies
RUN apk add python3 py3-pip supervisor curl gcc python3-dev musl-dev
# Create venv and install Django deps
RUN python3 -m venv /app/.venv
RUN /app/.venv/bin/pip install Django djangorestframework ...
# Copy React build from stage 1
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html
# Copy Django app, nginx config, supervisor config
COPY . /app
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/supervisord.conf
# Run supervisor to manage both nginx and Django
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
```

### Design Rationale: Deployment

**Why Docker multi-stage build?**
- **Minimizes image size**: Build tools (Node, npm) not present in production image
- **Separation of concerns**: Frontend build isolated from backend runtime
- **Cache efficiency**: npm dependencies cached separately from source changes

**Why nginx as reverse proxy?**
- **Performance**: nginx handles static files more efficiently than Django
- **SPA routing**: `try_files $uri $uri/ /index.html` enables client-side routing
- **URL rewriting**: Strips `/api/` prefix before proxying to Django, simplifying Django URL configuration
- **Correct DRF URL generation**: `proxy_set_header Host $host:$server_port` ensures Django REST Framework generates URLs with correct port number

**Why Supervisor for process management?**
- **Single container simplicity**: Manages both nginx and Django within one container
- **HuggingFace compatibility**: No need for docker-compose or separate containers
- **Automatic restarts**: Supervisor restarts crashed processes automatically
- **Unified logging**: Both processes log through supervisor

**Why SQLite instead of PostgreSQL?**
- **No external dependencies**: Entire app runs in single container
- **File-based persistence**: Database persists in container storage/volumes
- **HuggingFace Space compatible**: No managed database service required
- **Sufficient performance**: Read-heavy analytics queries perform well with indexes
- **Atomic transactions**: SQLite supports full ACID compliance for simulation integrity

---

## Backend Architecture

### Layered Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      REST API Layer (DRF)                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐ │
│  │ Profile ViewSet│  │ WallSection    │  │ Simulation         │ │
│  │ + simulate()   │  │ ViewSet (CRUD) │  │ Reporting Views    │ │
│  │ + overview()   │  │                │  │ + days endpoint    │ │
│  └───────┬────────┘  └────────────────┘  └──────────┬─────────┘ │
└──────────┼──────────────────────────────────────────┼────────────┘
           │                                          │
           ▼                                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐ │
│  │ ConfigParser   │  │ WallSimulator  │  │ Query Services     │ │
│  │ - Parse config │  │ - ThreadPool   │  │ - Daily ice usage  │ │
│  │ - Validation   │  │ - Simulation   │  │ - Cost overviews   │ │
│  └────────────────┘  └────────────────┘  └────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
           │                     │                     │
           ▼                     ▼                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                  Django ORM + SQLite Database                    │
│  ┌────────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐ │
│  │ Simulation │─▶│ Profile  │─▶│WallSection│─▶│DailyProgress │ │
│  └────────────┘  └──────────┘  └───────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**ViewSets** (`apps/profiles/views/`)
- HTTP request/response handling
- Request parameter extraction and validation
- Delegate business logic to services
- Serialize responses using DRF serializers

**Business Logic** (`apps/profiles/parsers.py`, `apps/profiles/services/simulator.py`)
- `ConfigParser`: Parse and validate multi-profile wall configurations
- `WallSimulator`: Execute simulation with ThreadPoolExecutor for parallel processing
- Service functions: Query aggregations, cost calculations, report generation

**Models** (`apps/profiles/models.py`)
- Django ORM model definitions
- Database constraints (unique_together, indexes)
- Foreign key relationships
- Auto timestamp fields (created_at, updated_at)

**Serializers** (`apps/profiles/serializers.py`)
- Data validation (field types, required fields, constraints)
- Auto-calculation of derived fields (ice_cubic_yards, cost_gold_dragons)
- JSON serialization/deserialization

### Design Rationale: Backend

**Why Django + Django REST Framework?**
- **Batteries included**: ORM, migrations, admin panel, authentication built-in
- **DRF ViewSets**: Automatic CRUD endpoints with minimal code
- **Serializers**: Data validation and transformation with declarative syntax
- **Mature ecosystem**: Well-tested, production-ready, extensive documentation

**Why service layer pattern?**
- **Separation of concerns**: Business logic isolated from HTTP/presentation layer
- **Testability**: Services can be unit tested without Django test client
- **Reusability**: Simulation logic can be called from management commands, celery tasks, etc.

**Why atomic transactions for simulation?**
- **Data integrity**: If simulation fails mid-run, entire operation rolls back
- **Consistency**: Database never left in partially-simulated state
- **Simplified error handling**: No need for manual cleanup on errors

```python
with transaction.atomic():
    simulation = Simulation.objects.create(...)
    result = simulator.simulate(profiles_config, start_date, simulation)
    simulation.total_days = result.total_days
    simulation.save()
    # If any exception occurs, entire transaction rolls back
```

---

## Frontend Architecture

### Component Structure

```
frontend/
├── src/
│   ├── pages/                 # Page-level components
│   │   ├── Dashboard.jsx      # Home page with simulations list
│   │   ├── SimulationForm.jsx # Run simulation form
│   │   └── SimulationResults.jsx # View simulation results + charts
│   ├── App.jsx                # Root component with navigation
│   ├── main.jsx               # Entry point
│   └── index.css              # Global styles + Tailwind import
├── public/
│   └── wall-constructor.png   # Logo
└── dist/                      # Built assets (npm run build)
```

### State Management Approach

**Hash-Based Routing** (no react-router)
```javascript
// App.jsx
const [route, setRoute] = useState(window.location.hash.slice(1) || 'dashboard')
const [params, setParams] = useState({})

useEffect(() => {
  const handleHashChange = () => {
    const hash = window.location.hash.slice(1)
    const [path, query] = hash.split('?')
    setRoute(path || 'dashboard')
    const searchParams = new URLSearchParams(query)
    // Parse params...
  }
  window.addEventListener('hashchange', handleHashChange)
  return () => window.removeEventListener('hashchange', handleHashChange)
}, [])
```

**Local State with useState**
- Each page manages its own state
- No global state management library (Redux, Zustand, etc.)
- Data fetched on component mount using native `fetch()`

### Design Rationale: Frontend

**Why hash-based routing instead of react-router?**
- **Zero dependencies**: Eliminates react-router dependency
- **Simple requirements**: Only 3 routes (dashboard, simulation, results)
- **No server configuration**: Works with any static file server
- **SPA fallback compatible**: nginx `try_files` works seamlessly

**Why no global state management?**
- **No shared state**: Each page operates independently
- **Simple data flow**: Simulations fetched fresh on each page load
- **Minimal complexity**: useState sufficient for local component state

**Why Tailwind CSS?**
- **Utility-first**: Rapid UI development without writing custom CSS
- **Small bundle**: PurgeCSS removes unused styles in production
- **Consistent design**: Design tokens (colors, spacing) centralized
- **No CSS modules needed**: Scoped styling via utility classes

**Why Recharts for visualization?**
- **React-native API**: Declarative, composable chart components
- **SVG-based**: Crisp rendering at any screen size
- **Responsive**: Automatic responsive sizing
- **No D3 knowledge required**: High-level abstractions over D3 primitives

---

## Data Model Design

### Entity-Relationship Diagram

```
┌─────────────────┐
│   Simulation    │
│ ───────────────  │  Primary entity tracking entire simulation run
│ id (PK)         │  - config_text: Original input configuration
│ config_text     │  - num_teams: Number of concurrent teams
│ num_teams       │  - start_date: Simulation start date
│ start_date      │  - total_days: Calculated after simulation
│ total_days      │  - total_cost: Sum of all daily progress costs
│ total_cost      │  - total_sections: Sum of all wall sections
│ total_sections  │
│ created_at      │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│    Profile      │
│ ─────────────── │  Wall construction profile (one per config line)
│ id (PK)         │  - simulation_id: Link to parent simulation
│ simulation_id   │  - name: "Profile 1", "Profile 2", etc.
│ name            │  - team_lead: "Team Lead 1", etc.
│ team_lead       │  - is_active: Enable/disable profile
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│  WallSection    │
│ ─────────────── │  Individual wall segment within a profile
│ id (PK)         │  - profile_id: Link to parent profile
│ profile_id      │  - section_name: "Section 1", "Section 2", etc.
│ section_name    │  - initial_height: Starting height (0-30 feet)
│ initial_height  │  - current_height: Updated during simulation
│ current_height  │
│ created_at      │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│ DailyProgress   │
│ ─────────────── │  Daily construction work on a wall section
│ id (PK)         │  - wall_section_id: Link to wall section
│ wall_section_id │  - date: Work date
│ date            │  - feet_built: Linear feet constructed
│ feet_built      │  - ice_cubic_yards: 195 yd³ per foot (auto-calculated)
│ ice_cubic_yards │  - cost_gold_dragons: 1900 GD per yd³ (auto-calculated)
│ cost_gold_dragons
│ notes           │
│ created_at      │
└─────────────────┘
```

### Design Rationale: Data Model

**Why Simulation as root entity?**
- **Isolation**: Each simulation run is independent and traceable
- **Reproducibility**: config_text stores exact input for replay
- **Aggregation**: total_days and total_cost calculated per simulation
- **History**: All simulations persist, enabling trend analysis

**Why Profile linked to Simulation?**
- **Multi-simulation support**: Same profile name can appear in multiple simulations
- **Data integrity**: Cascade delete removes all profiles when simulation deleted
- **Unique constraint**: `unique_together = [["simulation", "name"]]` prevents duplicate profile names within a simulation

**Why WallSection separate from Profile?**
- **Granular tracking**: Each section has independent initial/current height
- **Daily progress linkage**: DailyProgress records link to specific wall sections
- **Scalability**: Supports profiles with 2000+ sections per spec requirements

**Why DailyProgress tracks individual days?**
- **Audit trail**: Complete history of construction work
- **Time-series queries**: `WHERE date BETWEEN start AND end` for date range analytics
- **Unique constraint**: `unique_together = [["wall_section", "date"]]` prevents duplicate entries
- **Database indexes**: `Index(fields=["date"])` and `Index(fields=["wall_section", "date"])` optimize queries

**Why auto-calculate ice_cubic_yards and cost_gold_dragons?**
- **Data consistency**: Calculations always follow formula (195 yd³/ft, 1900 GD/yd³)
- **Denormalization for performance**: Avoids recalculating in every query
- **Single source of truth**: Constants defined in `apps/profiles/constants.py`

```python
# apps/profiles/serializers.py
def create(self, validated_data):
    feet_built = validated_data['feet_built']
    ice_cubic_yards = feet_built * ICE_PER_FOOT  # 195
    cost_gold_dragons = ice_cubic_yards * COST_PER_CUBIC_YARD  # 1900
    return DailyProgress.objects.create(
        **validated_data,
        ice_cubic_yards=ice_cubic_yards,
        cost_gold_dragons=cost_gold_dragons
    )
```

---

## Simulation Engine

### High-Level Flow

```
1. POST /api/profiles/simulate/
   ├─ Parse config_text → list[ProfileConfig]
   ├─ Validate heights (0-30), team count (1-1000)
   └─ Create Simulation record

2. WallSimulator.simulate()
   ├─ Initialize profiles and sections in database
   ├─ While any section < 30 feet:
   │  ├─ Assign work to teams (round-robin)
   │  ├─ Process sections in parallel (ThreadPoolExecutor)
   │  ├─ Save DailyProgress records (bulk_create)
   │  └─ Update section current_height
   └─ Calculate totals and return summary

3. Update Simulation record with totals
   └─ Return response with simulation_id
```

### ConfigParser Implementation

**Input Format**
```
21 25 28
17
17 22 17 19 17
```
- Each line = 1 profile
- Space-separated integers = wall section heights (0-30 feet)
- Empty lines ignored
- Whitespace trimmed

**Validation Logic** (`apps/profiles/parsers.py`)
```python
class ConfigParser:
    @staticmethod
    def _validate_heights(heights: list[int], line_num: int) -> None:
        if not heights:
            raise ValueError(f"Line {line_num}: No heights specified")

        for height in heights:
            if not MIN_HEIGHT <= height <= MAX_HEIGHT:  # 0-30
                raise ValueError(f"Line {line_num}: Height {height} out of range")

        if len(heights) > MAX_SECTIONS_PER_PROFILE:  # 2000
            raise ValueError(f"Line {line_num}: Too many sections")

    @staticmethod
    def _validate_needs_construction(profiles: list[ProfileConfig]) -> None:
        all_at_target = all(
            height == TARGET_HEIGHT  # 30
            for profile in profiles
            for height in profile.heights
        )
        if all_at_target:
            raise ValueError("All sections already at target height, no work needed")
```

**Design Rationale: Config Validation**

**Why validate at parse time?**
- **Fail fast**: Errors reported immediately before simulation starts
- **Clear error messages**: Line numbers and specific validation failures
- **Transaction safety**: Parser errors prevent database writes

**Why reject configs with all sections at 30 feet?**
- **User experience**: Input "30 30 30" would return 0 days, 0 cost (confusing)
- **Explicit intent**: Forces user to provide sections requiring construction
- **Edge case handling**: Prevents misleading results

### WallSimulator Implementation

**Parallelization Strategy** (`apps/profiles/services/simulator.py`)
```python
class WallSimulator:
    def __init__(self, num_teams: int):
        self.num_teams = num_teams
        # No ThreadPoolExecutor created here - uses as_completed pattern instead

    def _process_day(self, sections: list[SectionData], day: int) -> list[ProcessingResult]:
        with ThreadPoolExecutor(max_workers=self.num_teams) as executor:
            futures = {
                executor.submit(self._process_section, section, day, team_id): section
                for team_id, section in enumerate(sections)
            }

            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        return results

    def _process_section(self, section: SectionData, day: int, team_id: int) -> ProcessingResult:
        # Worker function - NO DATABASE ACCESS
        # - Calculate feet_built, ice, cost
        # - Write team log to file
        # - Return ProcessingResult with calculations
        pass
```

**Design Rationale: Simulation Engine**

**Why ThreadPoolExecutor instead of multiprocessing?**
- **I/O-bound workload**: File writes dominate, GIL not a bottleneck
- **Simpler data sharing**: SectionData passed by reference, no pickling
- **Lower overhead**: Threads cheaper than processes
- **SQLite compatibility**: Multi-process writes require WAL mode and careful locking

**Why process sections in parallel but save to DB in main thread?**
- **SQLite single-writer constraint**: Multiple threads writing causes `SQLITE_BUSY` errors
- **Atomic transaction**: All progress for a day saved in single bulk_create()
- **Separation of concerns**: Workers calculate, main thread persists

**Why log to individual team files instead of database?**
- **Spec requirement**: Team logs written to `logs/team_{N}.log`
- **Performance**: File I/O in threads, no database contention
- **Debugging**: Easy to inspect team activity without database queries

**Why assign work round-robin?**
- **Fairness**: All incomplete sections get equal team assignment priority
- **Load balancing**: Teams distributed evenly across sections
- **Predictable behavior**: Deterministic assignment order for testing

---

## API Design

### RESTful Endpoints

**Simulation**
- `POST /api/profiles/simulate/` - Run simulation from config

**Overview/Reporting**
- `GET /api/profiles/overview/` - Total cost across all simulations
- `GET /api/profiles/overview/{day}/` - Cost for specific day (all profiles)
- `GET /api/profiles/{id}/overview/{day}/` - Cost for specific day (single profile)
- `GET /api/profiles/{id}/days/{day}/` - Ice usage breakdown for day

**CRUD Operations**
- Profiles: `GET|POST|PUT|PATCH|DELETE /api/profiles/`
- WallSections: `GET|POST|PUT|DELETE /api/wallsections/`
- DailyProgress: `GET|POST|PUT|DELETE /api/progress/`

### URL Generation Issue & Solution

**Problem**: Django REST Framework generates incorrect URLs when behind nginx reverse proxy

```
# Incorrect URL (missing port)
http://46.10.161.171/api/profiles/

# Expected URL
http://46.10.161.171:7860/api/profiles/
```

**Root Cause**: nginx `proxy_set_header Host $host;` sends hostname without port

**Solution**: Configure nginx to include port in Host header
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host:$server_port;  # Include port!
    proxy_set_header X-Forwarded-Port $server_port;
}
```

```python
# config/settings/base.py
USE_X_FORWARDED_PORT = True  # Trust X-Forwarded-Port header
```

### Design Rationale: API

**Why custom action for simulation instead of POST /api/simulations/?**
- **Semantic clarity**: `/api/profiles/simulate/` clearly indicates simulation operation
- **Parameter validation**: Custom serializer for config, num_teams, start_date
- **Response structure**: Returns simulation summary, not standard CRUD response

**Why separate overview endpoints for day-specific vs total?**
- **Query optimization**: Different aggregation queries for day-specific vs total
- **REST semantics**: `/overview/` = total, `/overview/{day}/` = specific day
- **Frontend flexibility**: Dashboard can request day-specific data without filtering

**Why filter DailyProgress by simulation in totals calculation?**
- **Data isolation**: Each simulation's totals independent of others
- **Bug prevention**: Fixed critical bug where totals accumulated across simulations

```python
# BEFORE (BUG): Summed ALL DailyProgress records
total_ice = sum(DailyProgress.objects.all().values_list("ice_cubic_yards", flat=True))

# AFTER (FIX): Filter by current simulation
wall_sections = WallSection.objects.filter(profile__simulation=simulation)
total_ice = sum(DailyProgress.objects.filter(wall_section__in=wall_sections).values_list("ice_cubic_yards", flat=True))
```

---

## Design Decisions & Rationale

### 1. Single Container Deployment

**Decision**: Package frontend + backend + database in one Docker container

**Alternatives Considered**:
- Separate containers for frontend, backend, database (docker-compose)
- Frontend served by CDN, backend as separate service
- Serverless deployment (AWS Lambda, etc.)

**Rationale**:
- ✅ **HuggingFace Space compatibility**: Platform expects single Dockerfile
- ✅ **Simplified deployment**: No orchestration, networking, or service discovery
- ✅ **Lower resource usage**: Single process supervisor, one SQLite file
- ✅ **Faster startup**: No inter-container communication overhead
- ❌ **Scaling limitations**: Cannot scale frontend and backend independently
- ❌ **Resource contention**: nginx and Django compete for container CPU/memory

**Conclusion**: Single container optimal for demo/prototype deployment on resource-constrained platforms

---

### 2. SQLite Instead of PostgreSQL

**Decision**: Use file-based SQLite database

**Alternatives Considered**:
- PostgreSQL managed service (AWS RDS, Heroku Postgres)
- PostgreSQL container via docker-compose
- MySQL/MariaDB

**Rationale**:
- ✅ **Zero configuration**: No connection strings, no user management
- ✅ **File-based persistence**: `db.sqlite3` stored in container volume
- ✅ **Adequate performance**: Indexes on date and wall_section_id handle analytics queries
- ✅ **ACID compliance**: Full transaction support with `BEGIN EXCLUSIVE`
- ✅ **Deployment simplicity**: No external database service required
- ❌ **Concurrency limitations**: Single writer, readers block during writes
- ❌ **No replication**: Backups require file-level copy

**Conclusion**: SQLite sufficient for single-instance deployment with moderate traffic

---

### 3. Multi-Threading vs Async/Await

**Decision**: Use ThreadPoolExecutor for parallel simulation

**Alternatives Considered**:
- asyncio with async/await syntax
- multiprocessing.Pool for CPU parallelism
- Celery task queue for distributed processing

**Rationale**:
- ✅ **I/O-bound workload**: File writes dominate, GIL not a bottleneck
- ✅ **Simpler code**: Synchronous functions easier to reason about
- ✅ **SQLite compatibility**: Threads share database connection pool
- ✅ **Lower overhead**: Threads cheaper than processes or async event loop
- ❌ **Not suitable for CPU-bound work**: GIL would limit parallelism
- ❌ **Blocking operations**: File I/O blocks threads

**Conclusion**: Threads optimal for I/O-bound simulation with SQLite backend

---

### 4. Validation at Parse Time

**Decision**: Validate all config inputs in ConfigParser before simulation

**Alternatives Considered**:
- Validate in Django serializer
- Validate in database constraints
- Validate during simulation execution

**Rationale**:
- ✅ **Fail fast**: Errors reported immediately, no database writes
- ✅ **Clear error messages**: Line numbers and specific validation failures
- ✅ **Separation of concerns**: Parser responsible for config validation
- ✅ **Testability**: Parser unit tested independently of Django
- ❌ **Duplicated validation**: Some checks also in database constraints

**Conclusion**: Early validation provides best user experience and prevents invalid simulations

---

### 5. Hash-Based Routing

**Decision**: Use hash-based routing (`#/dashboard`, `#/results`) instead of HTML5 History API

**Alternatives Considered**:
- react-router with BrowserRouter (History API)
- Server-side routing (Django templates)

**Rationale**:
- ✅ **Zero dependencies**: No react-router library
- ✅ **nginx compatibility**: `try_files` fallback works without server configuration
- ✅ **Simple requirements**: Only 3 routes needed
- ✅ **No server config**: Works with any static file server
- ❌ **Ugly URLs**: `#/dashboard` instead of `/dashboard`
- ❌ **No SSR**: Client-side rendering only

**Conclusion**: Hash routing sufficient for single-page app with minimal routes

---

### 6. Logo Placement in Frontend

**Decision**: Store logo in `frontend/public/` and reference as `/wall-constructor.png`

**Alternatives Considered**:
- Import logo as React component (SVG)
- Store in `frontend/src/assets/` and import via Vite
- Base64 encode logo in CSS

**Rationale**:
- ✅ **Vite automatic copy**: Files in `public/` copied to `dist/` during build
- ✅ **Simple references**: `<img src="/wall-constructor.png" />` works in production
- ✅ **Cacheable**: Browser caches static image separately from JS bundle
- ✅ **No build transformation**: PNG served as-is, no compression/optimization
- ❌ **Not tree-shakeable**: Logo included even if unused

**Conclusion**: Public directory optimal for static assets referenced by absolute path

---

## Summary

This architecture achieves the following goals:

1. **Single-container deployment** compatible with HuggingFace Spaces
2. **File-based persistence** with no external service dependencies
3. **Multi-threaded simulation** for concurrent team processing
4. **RESTful API** with automatic CRUD and custom simulation endpoints
5. **Minimal frontend dependencies** (React, Tailwind, Recharts only)
6. **Production-ready** with comprehensive validation, error handling, and testing

The design prioritizes simplicity, deployability, and maintainability over premature optimization or unnecessary complexity.
