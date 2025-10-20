# Wall Construction API - Test-Driven Development Specification

## Philosophy: Test-First Development

This specification defines a comprehensive test-driven development (TDD) strategy for the Wall Construction API. Every feature begins with tests, follows the Red-Green-Refactor cycle, and maintains high code coverage without sacrificing code quality.

**Core Principle**: Write the test first, watch it fail, make it pass, then refactor. No production code without a failing test.

---

## TDD Cycle

### The Red-Green-Refactor Loop

```
1. 🔴 RED:    Write a failing test
              ↓
2. 🟢 GREEN:  Write minimal code to pass
              ↓
3. 🔵 REFACTOR: Improve code quality
              ↓
              (repeat)
```

### Workflow Example

```python
# Step 1: RED - Write failing test
def test_ice_usage_calculation():
    calculator = IceUsageCalculator()
    result = calculator.calculate_ice_usage(Decimal("10.0"))
    assert result == Decimal("1950.00")  # 10 feet * 195 yd³/ft

# Run test → FAIL (IceUsageCalculator doesn't exist)

# Step 2: GREEN - Minimal implementation
class IceUsageCalculator:
    ICE_PER_FOOT = Decimal("195")

    def calculate_ice_usage(self, feet_built):
        return feet_built * self.ICE_PER_FOOT

# Run test → PASS

# Step 3: REFACTOR - Improve (if needed)
# Add type hints, docstrings, extract constants
```

---

## Test Pyramid

```
         ╱╲
        ╱  ╲
       ╱ E2E ╲        ← Few: Full user flows (10%)
      ╱────────╲
     ╱          ╲
    ╱ Integration╲    ← Some: API endpoints (30%)
   ╱──────────────╲
  ╱                ╲
 ╱  Unit Tests      ╲  ← Many: Models, services, utils (60%)
╱────────────────────╲
```

### Test Distribution

- **Unit Tests (60%)**: Fast, isolated, test single functions/methods
- **Integration Tests (30%)**: Test component interactions (API + DB)
- **E2E Tests (10%)**: Full workflows from HTTP request to response

---

## Test Stack

### Dependencies

**Required**:
```toml
[project.optional-dependencies]
test = [
  "pytest==8.4.2",
  "pytest-django==4.9.0",
  "pytest-xdist==3.6.1",       # Parallel test execution
  "factory-boy==3.3.1",
  "Faker==33.3.0",
]
```

**Optional (Coverage)**:
```toml
coverage = [
  "pytest-cov==6.0.0",
  "coverage[toml]==7.6.0",
]
```

### Why These Tools?

- **pytest**: Modern test runner, better fixtures than unittest
- **pytest-django**: Django integration (@pytest.mark.django_db)
- **factory-boy**: Test data factories (replaces fixtures.json)
- **Faker**: Realistic fake data (names, dates, text)
- **pytest-xdist**: Run tests in parallel (faster CI)
- **pytest-cov**: Code coverage reporting

---

## Project Structure

```
wall-construction-api/
├── apps/
│   ├── profiles/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py
│   │   └── repositories.py
│   └── progress/
│       ├── models.py
│       ├── serializers.py
│       └── views.py
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── factories.py             # Model factories
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_models.py       # Model tests
│   │   ├── test_services.py     # Service layer tests
│   │   ├── test_repositories.py # Repository tests
│   │   └── test_utils.py        # Utility function tests
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_profiles.py
│   │   ├── test_api_progress.py
│   │   └── test_api_analytics.py
│   └── e2e/
│       ├── __init__.py
│       └── test_workflows.py    # Full user workflows
├── pytest.ini
└── pyproject.toml
```

---

## Configuration

### pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Enable django-db access
addopts =
    --strict-markers
    --tb=short
    --reuse-db
    --nomigrations
    -v

# Coverage settings
    --cov=apps
    --cov-report=term-missing:skip-covered
    --cov-report=html
    --cov-fail-under=90

markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (API + DB)
    e2e: End-to-end tests (full workflows)
    slow: Slow tests (run separately)

# Parallel execution
    -n auto

# Django settings
testpaths = tests
```

### pyproject.toml (test settings)

```toml
[tool.coverage.run]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/admin.py",
    "*/apps.py",
    "manage.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

---

## Fixtures and Factories

### conftest.py (Shared Fixtures)

```python
# tests/conftest.py
import pytest
from rest_framework.test import APIClient
from decimal import Decimal

# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, profile_factory):
    """Authenticated API client (if auth is added later)."""
    # For now, no auth required
    return api_client


# ============================================================================
# Constants Fixtures
# ============================================================================

@pytest.fixture
def ice_per_foot():
    """Ice consumption constant: 195 cubic yards per foot."""
    return Decimal("195")


@pytest.fixture
def cost_per_yard():
    """Ice cost constant: 1,900 Gold Dragons per cubic yard."""
    return Decimal("1900")


# ============================================================================
# Date Fixtures
# ============================================================================

@pytest.fixture
def today():
    """Today's date."""
    from datetime.date import today
    return today()


@pytest.fixture
def date_range():
    """Sample date range for testing."""
    from datetime import date
    return {
        "start": date(2025, 10, 1),
        "end": date(2025, 10, 15)
    }
```

### factories.py (Model Factories)

```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal
from datetime import date

from apps.profiles.models import Profile, WallSection, DailyProgress

fake = Faker()

# ============================================================================
# Profile Factory
# ============================================================================

class ProfileFactory(DjangoModelFactory):
    """Factory for creating Profile instances."""

    class Meta:
        model = Profile
        django_get_or_create = ("name",)  # Avoid unique constraint errors

    name = factory.Sequence(lambda n: f"Profile {n}")
    team_lead = factory.Faker("name")
    is_active = True


# ============================================================================
# WallSection Factory
# ============================================================================

class WallSectionFactory(DjangoModelFactory):
    """Factory for creating WallSection instances."""

    class Meta:
        model = WallSection
        django_get_or_create = ("profile", "section_name")

    profile = factory.SubFactory(ProfileFactory)
    section_name = factory.Sequence(lambda n: f"Section {n}")
    start_position = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True
    )
    target_length_feet = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=100,
        max_value=1000
    )


# ============================================================================
# DailyProgress Factory
# ============================================================================

class DailyProgressFactory(DjangoModelFactory):
    """Factory for creating DailyProgress instances."""

    class Meta:
        model = DailyProgress
        django_get_or_create = ("wall_section", "date")

    wall_section = factory.SubFactory(WallSectionFactory)
    date = factory.LazyFunction(date.today)
    feet_built = factory.Faker(
        "pydecimal",
        left_digits=3,
        right_digits=2,
        positive=True,
        min_value=1,
        max_value=50
    )

    # Auto-calculate ice and cost based on feet_built
    ice_cubic_yards = factory.LazyAttribute(
        lambda obj: obj.feet_built * Decimal("195")
    )
    cost_gold_dragons = factory.LazyAttribute(
        lambda obj: obj.ice_cubic_yards * Decimal("1900")
    )

    notes = factory.Faker("sentence")


# ============================================================================
# Factory Traits (Variants)
# ============================================================================

class ProfileFactory_Inactive(ProfileFactory):
    """Inactive profile variant."""
    is_active = False


class DailyProgressFactory_ZeroProgress(DailyProgressFactory):
    """Zero progress variant (edge case)."""
    feet_built = Decimal("0.00")
    ice_cubic_yards = Decimal("0.00")
    cost_gold_dragons = Decimal("0.00")
    notes = "No work done today"
```

---

## Unit Tests

### Test Models

```python
# tests/unit/test_models.py
import pytest
from decimal import Decimal
from datetime import date

from apps.profiles.models import Profile, WallSection, DailyProgress
from tests.factories import (
    ProfileFactory,
    WallSectionFactory,
    DailyProgressFactory
)

# ============================================================================
# Profile Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestProfileModel:
    """Test Profile model validation and behavior."""

    def test_create_profile_with_valid_data(self):
        """Should create profile with valid data."""
        profile = ProfileFactory(
            name="Northern Watch",
            team_lead="Jon Snow"
        )

        assert profile.id is not None
        assert profile.name == "Northern Watch"
        assert profile.team_lead == "Jon Snow"
        assert profile.is_active is True

    def test_profile_name_must_be_unique(self):
        """Should raise error when creating duplicate profile name."""
        ProfileFactory(name="Northern Watch")

        with pytest.raises(Exception):  # IntegrityError
            ProfileFactory(name="Northern Watch")

    def test_profile_ordering_by_created_at_desc(self):
        """Should order profiles by created_at descending."""
        profile1 = ProfileFactory(name="First")
        profile2 = ProfileFactory(name="Second")
        profile3 = ProfileFactory(name="Third")

        profiles = Profile.objects.all()
        assert profiles[0] == profile3  # Most recent first
        assert profiles[1] == profile2
        assert profiles[2] == profile1

    def test_profile_string_representation(self):
        """Should return profile name as string."""
        profile = ProfileFactory(name="Northern Watch")
        assert str(profile) == "Northern Watch"


# ============================================================================
# WallSection Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestWallSectionModel:
    """Test WallSection model validation and behavior."""

    def test_create_wall_section_with_valid_data(self):
        """Should create wall section with valid data."""
        profile = ProfileFactory()
        section = WallSectionFactory(
            profile=profile,
            section_name="Tower 1-2",
            start_position=Decimal("0.00"),
            target_length_feet=Decimal("500.00")
        )

        assert section.id is not None
        assert section.profile == profile
        assert section.section_name == "Tower 1-2"

    def test_unique_together_profile_section_name(self):
        """Should enforce unique constraint on (profile, section_name)."""
        profile = ProfileFactory()
        WallSectionFactory(profile=profile, section_name="Tower 1-2")

        with pytest.raises(Exception):  # IntegrityError
            WallSectionFactory(profile=profile, section_name="Tower 1-2")

    def test_different_profiles_can_have_same_section_name(self):
        """Different profiles can use the same section name."""
        profile1 = ProfileFactory(name="Profile 1")
        profile2 = ProfileFactory(name="Profile 2")

        section1 = WallSectionFactory(profile=profile1, section_name="Tower 1")
        section2 = WallSectionFactory(profile=profile2, section_name="Tower 1")

        assert section1.section_name == section2.section_name
        assert section1.profile != section2.profile

    def test_cascade_delete_when_profile_deleted(self):
        """Should delete wall sections when profile is deleted."""
        profile = ProfileFactory()
        section = WallSectionFactory(profile=profile)
        section_id = section.id

        profile.delete()

        assert not WallSection.objects.filter(id=section_id).exists()


# ============================================================================
# DailyProgress Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestDailyProgressModel:
    """Test DailyProgress model validation and calculations."""

    def test_create_daily_progress_with_valid_data(self):
        """Should create daily progress with valid data."""
        section = WallSectionFactory()
        progress = DailyProgressFactory(
            wall_section=section,
            date=date(2025, 10, 15),
            feet_built=Decimal("12.50"),
            ice_cubic_yards=Decimal("2437.50"),
            cost_gold_dragons=Decimal("4631250.00")
        )

        assert progress.id is not None
        assert progress.feet_built == Decimal("12.50")
        assert progress.ice_cubic_yards == Decimal("2437.50")
        assert progress.cost_gold_dragons == Decimal("4631250.00")

    def test_unique_together_wall_section_date(self):
        """Should enforce unique constraint on (wall_section, date)."""
        section = WallSectionFactory()
        today = date.today()

        DailyProgressFactory(wall_section=section, date=today)

        with pytest.raises(Exception):  # IntegrityError
            DailyProgressFactory(wall_section=section, date=today)

    def test_ordering_by_date_descending(self):
        """Should order progress by date descending."""
        section = WallSectionFactory()
        progress1 = DailyProgressFactory(
            wall_section=section,
            date=date(2025, 10, 1)
        )
        progress2 = DailyProgressFactory(
            wall_section=section,
            date=date(2025, 10, 15)
        )

        progress_list = DailyProgress.objects.filter(wall_section=section)
        assert progress_list[0] == progress2  # Most recent first
        assert progress_list[1] == progress1

    @pytest.mark.parametrize("feet,expected_ice", [
        (Decimal("10.00"), Decimal("1950.00")),
        (Decimal("0.00"), Decimal("0.00")),
        (Decimal("1.00"), Decimal("195.00")),
        (Decimal("100.50"), Decimal("19597.50")),
    ])
    def test_ice_calculation_formula(self, feet, expected_ice):
        """Should correctly calculate ice usage (195 yd³ per foot)."""
        calculated_ice = feet * Decimal("195")
        assert calculated_ice == expected_ice

    @pytest.mark.parametrize("ice,expected_cost", [
        (Decimal("195.00"), Decimal("370500.00")),
        (Decimal("0.00"), Decimal("0.00")),
        (Decimal("1950.00"), Decimal("3705000.00")),
    ])
    def test_cost_calculation_formula(self, ice, expected_cost):
        """Should correctly calculate cost (1900 GD per yd³)."""
        calculated_cost = ice * Decimal("1900")
        assert calculated_cost == expected_cost
```

### Test Services

```python
# tests/unit/test_services.py
import pytest
from decimal import Decimal
from datetime import date

from apps.profiles.services import IceUsageCalculator, CostAggregator
from tests.factories import ProfileFactory, WallSectionFactory, DailyProgressFactory

# ============================================================================
# IceUsageCalculator Tests
# ============================================================================

@pytest.mark.unit
class TestIceUsageCalculator:
    """Test IceUsageCalculator service."""

    @pytest.fixture
    def calculator(self):
        return IceUsageCalculator()

    def test_calculate_ice_usage_standard_value(self, calculator):
        """Should calculate ice usage for standard value."""
        result = calculator.calculate_ice_usage(Decimal("10.0"))
        expected = Decimal("1950.00")
        assert result == expected

    def test_calculate_ice_usage_zero_feet(self, calculator):
        """Should return zero for zero feet built."""
        result = calculator.calculate_ice_usage(Decimal("0.00"))
        assert result == Decimal("0.00")

    def test_calculate_ice_usage_decimal_precision(self, calculator):
        """Should handle decimal precision correctly."""
        result = calculator.calculate_ice_usage(Decimal("12.50"))
        expected = Decimal("2437.50")
        assert result == expected

    def test_calculate_cost_standard_value(self, calculator):
        """Should calculate cost for standard ice amount."""
        ice = Decimal("1950.00")
        result = calculator.calculate_cost(ice)
        expected = Decimal("3705000.00")
        assert result == expected

    def test_calculate_cost_zero_ice(self, calculator):
        """Should return zero cost for zero ice."""
        result = calculator.calculate_cost(Decimal("0.00"))
        assert result == Decimal("0.00")

    def test_calculate_full_cost_returns_tuple(self, calculator):
        """Should return (ice, cost) tuple."""
        ice, cost = calculator.calculate_full_cost(Decimal("10.00"))
        assert ice == Decimal("1950.00")
        assert cost == Decimal("3705000.00")

    def test_constants_are_correct(self, calculator):
        """Should have correct constant values."""
        assert calculator.ICE_PER_FOOT == Decimal("195")
        assert calculator.COST_PER_CUBIC_YARD == Decimal("1900")


# ============================================================================
# CostAggregator Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.django_db
class TestCostAggregator:
    """Test CostAggregator service."""

    @pytest.fixture
    def aggregator(self):
        return CostAggregator(max_workers=2)

    def test_calculate_profile_cost_single_progress(self, aggregator):
        """Should calculate cost for single progress entry."""
        profile = ProfileFactory()
        section = WallSectionFactory(profile=profile)
        DailyProgressFactory(
            wall_section=section,
            date=date(2025, 10, 15),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00")
        )

        result = aggregator.calculate_profile_cost(
            profile.id,
            "2025-10-15",
            "2025-10-15"
        )

        assert result["total_feet_built"] == "10.00"
        assert result["total_ice_cubic_yards"] == "1950.00"
        assert result["total_cost_gold_dragons"] == "3705000.00"

    def test_calculate_multi_profile_costs_parallel(self, aggregator):
        """Should calculate costs for multiple profiles in parallel."""
        profile1 = ProfileFactory(name="Profile 1")
        profile2 = ProfileFactory(name="Profile 2")

        section1 = WallSectionFactory(profile=profile1)
        section2 = WallSectionFactory(profile=profile2)

        DailyProgressFactory(wall_section=section1, feet_built=Decimal("10.00"))
        DailyProgressFactory(wall_section=section2, feet_built=Decimal("20.00"))

        results = aggregator.calculate_multi_profile_costs(
            [profile1.id, profile2.id],
            "2025-10-01",
            "2025-10-31"
        )

        assert len(results) == 2
        assert all("total_cost_gold_dragons" in r for r in results)

    def test_shutdown_executor(self, aggregator):
        """Should gracefully shutdown thread pool."""
        aggregator.shutdown()
        # No exception should be raised
```

### Test Repositories

```python
# tests/unit/test_repositories.py
import pytest
from decimal import Decimal
from datetime import date

from apps.profiles.repositories import DailyProgressRepository
from tests.factories import ProfileFactory, WallSectionFactory, DailyProgressFactory

@pytest.mark.unit
@pytest.mark.django_db
class TestDailyProgressRepository:
    """Test DailyProgressRepository data access layer."""

    @pytest.fixture
    def repository(self):
        return DailyProgressRepository()

    def test_get_by_date_returns_progress_for_date(self, repository):
        """Should return all progress for a specific date."""
        profile = ProfileFactory()
        section1 = WallSectionFactory(profile=profile, section_name="Section 1")
        section2 = WallSectionFactory(profile=profile, section_name="Section 2")

        target_date = date(2025, 10, 15)
        other_date = date(2025, 10, 14)

        progress1 = DailyProgressFactory(wall_section=section1, date=target_date)
        progress2 = DailyProgressFactory(wall_section=section2, date=target_date)
        DailyProgressFactory(wall_section=section1, date=other_date)  # Should not be returned

        results = repository.get_by_date(profile.id, target_date)

        assert results.count() == 2
        assert progress1 in results
        assert progress2 in results

    def test_get_aggregates_by_profile_sums_correctly(self, repository):
        """Should aggregate totals correctly."""
        profile = ProfileFactory()
        section = WallSectionFactory(profile=profile)

        DailyProgressFactory(
            wall_section=section,
            date=date(2025, 10, 1),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00")
        )
        DailyProgressFactory(
            wall_section=section,
            date=date(2025, 10, 2),
            feet_built=Decimal("15.00"),
            ice_cubic_yards=Decimal("2925.00"),
            cost_gold_dragons=Decimal("5557500.00")
        )

        result = repository.get_aggregates_by_profile(
            profile.id,
            "2025-10-01",
            "2025-10-02"
        )

        assert result["total_feet"] == Decimal("25.00")
        assert result["total_ice"] == Decimal("4875.00")
        assert result["total_cost"] == Decimal("9262500.00")
        assert result["record_count"] == 2

    def test_get_aggregates_empty_queryset_returns_zeros(self, repository):
        """Should return zeros for empty queryset."""
        profile = ProfileFactory()

        result = repository.get_aggregates_by_profile(
            profile.id,
            "2025-10-01",
            "2025-10-31"
        )

        assert result["total_feet"] == Decimal("0")
        assert result["total_ice"] == Decimal("0")
        assert result["total_cost"] == Decimal("0")
        assert result["record_count"] == 0
```

---

## Integration Tests (API)

### Test Profile API

```python
# tests/integration/test_api_profiles.py
import pytest
from rest_framework import status
from django.urls import reverse

from tests.factories import ProfileFactory

@pytest.mark.integration
@pytest.mark.django_db
class TestProfileListAPI:
    """Test GET /api/profiles/ endpoint."""

    @pytest.fixture
    def url(self):
        return reverse("profile-list")

    def test_list_profiles_returns_200(self, api_client, url):
        """Should return 200 OK."""
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_profiles_returns_pagination(self, api_client, url):
        """Should return paginated response."""
        ProfileFactory.create_batch(5)

        response = api_client.get(url)
        data = response.json()

        assert "count" in data
        assert "results" in data
        assert data["count"] == 5
        assert len(data["results"]) == 5

    def test_list_profiles_filters_by_active(self, api_client, url):
        """Should filter by is_active parameter."""
        ProfileFactory(name="Active", is_active=True)
        ProfileFactory(name="Inactive", is_active=False)

        response = api_client.get(url, {"is_active": "true"})
        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["name"] == "Active"

    def test_list_profiles_ordered_by_created_desc(self, api_client, url):
        """Should order profiles by created_at descending."""
        profile1 = ProfileFactory(name="First")
        profile2 = ProfileFactory(name="Second")
        profile3 = ProfileFactory(name="Third")

        response = api_client.get(url)
        data = response.json()

        assert data["results"][0]["name"] == "Third"
        assert data["results"][1]["name"] == "Second"
        assert data["results"][2]["name"] == "First"


@pytest.mark.integration
@pytest.mark.django_db
class TestProfileCreateAPI:
    """Test POST /api/profiles/ endpoint."""

    @pytest.fixture
    def url(self):
        return reverse("profile-list")

    def test_create_profile_with_valid_data(self, api_client, url):
        """Should create profile with valid data."""
        payload = {
            "name": "Northern Watch",
            "team_lead": "Jon Snow",
            "is_active": True
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Northern Watch"
        assert data["team_lead"] == "Jon Snow"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_profile_with_duplicate_name_fails(self, api_client, url):
        """Should return 400 for duplicate name."""
        ProfileFactory(name="Northern Watch")

        payload = {
            "name": "Northern Watch",
            "team_lead": "Jon Snow"
        }

        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_profile_with_missing_name_fails(self, api_client, url):
        """Should return 400 for missing required field."""
        payload = {
            "team_lead": "Jon Snow"
        }

        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.json()
```

### Test Progress API

```python
# tests/integration/test_api_progress.py
import pytest
from decimal import Decimal
from datetime import date
from rest_framework import status
from django.urls import reverse

from tests.factories import ProfileFactory, WallSectionFactory, DailyProgressFactory

@pytest.mark.integration
@pytest.mark.django_db
class TestRecordProgressAPI:
    """Test POST /api/profiles/{id}/progress/ endpoint."""

    def test_record_progress_with_valid_data(self, api_client):
        """Should record progress and auto-calculate ice/cost."""
        profile = ProfileFactory()
        section = WallSectionFactory(profile=profile)

        url = reverse("profile-progress", kwargs={"pk": profile.id})
        payload = {
            "wall_section_id": section.id,
            "date": "2025-10-15",
            "feet_built": "12.50",
            "notes": "Good progress today"
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["feet_built"] == "12.50"
        assert data["ice_cubic_yards"] == "2437.50"  # 12.5 * 195
        assert data["cost_gold_dragons"] == "4631250.00"  # 2437.5 * 1900

    def test_record_progress_for_same_section_and_date_fails(self, api_client):
        """Should return 400 for duplicate (section, date)."""
        profile = ProfileFactory()
        section = WallSectionFactory(profile=profile)
        today = date.today()

        DailyProgressFactory(wall_section=section, date=today)

        url = reverse("profile-progress", kwargs={"pk": profile.id})
        payload = {
            "wall_section_id": section.id,
            "date": str(today),
            "feet_built": "10.00"
        }

        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_record_progress_with_zero_feet_allowed(self, api_client):
        """Should allow zero feet built (no work day)."""
        profile = ProfileFactory()
        section = WallSectionFactory(profile=profile)

        url = reverse("profile-progress", kwargs={"pk": profile.id})
        payload = {
            "wall_section_id": section.id,
            "date": "2025-10-15",
            "feet_built": "0.00",
            "notes": "No work today"
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["feet_built"] == "0.00"
        assert data["ice_cubic_yards"] == "0.00"
        assert data["cost_gold_dragons"] == "0.00"
```

### Test Analytics API

```python
# tests/integration/test_api_analytics.py
import pytest
from decimal import Decimal
from datetime import date
from rest_framework import status
from django.urls import reverse

from tests.factories import ProfileFactory, WallSectionFactory, DailyProgressFactory

@pytest.mark.integration
@pytest.mark.django_db
class TestDailyIceUsageAPI:
    """Test GET /api/profiles/{id}/daily-ice-usage/?date=YYYY-MM-DD"""

    def test_daily_ice_usage_returns_breakdown(self, api_client):
        """Should return daily ice usage breakdown by section."""
        profile = ProfileFactory()
        section1 = WallSectionFactory(profile=profile, section_name="Tower 1-2")
        section2 = WallSectionFactory(profile=profile, section_name="Tower 2-3")

        target_date = date(2025, 10, 15)
        DailyProgressFactory(
            wall_section=section1,
            date=target_date,
            feet_built=Decimal("12.50"),
            ice_cubic_yards=Decimal("2437.50")
        )
        DailyProgressFactory(
            wall_section=section2,
            date=target_date,
            feet_built=Decimal("16.25"),
            ice_cubic_yards=Decimal("3168.75")
        )

        url = reverse("profile-daily-ice-usage", kwargs={"pk": profile.id})
        response = api_client.get(url, {"date": "2025-10-15"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_feet_built"] == "28.75"
        assert data["total_ice_cubic_yards"] == "5606.25"
        assert len(data["sections"]) == 2


@pytest.mark.integration
@pytest.mark.django_db
class TestCostOverviewAPI:
    """Test GET /api/profiles/{id}/cost-overview/?start_date&end_date"""

    def test_cost_overview_returns_summary_and_breakdown(self, api_client):
        """Should return summary stats and daily breakdown."""
        profile = ProfileFactory()
        section = WallSectionFactory(profile=profile)

        DailyProgressFactory(
            wall_section=section,
            date=date(2025, 10, 1),
            feet_built=Decimal("10.00"),
            ice_cubic_yards=Decimal("1950.00"),
            cost_gold_dragons=Decimal("3705000.00")
        )
        DailyProgressFactory(
            wall_section=section,
            date=date(2025, 10, 2),
            feet_built=Decimal("15.00"),
            ice_cubic_yards=Decimal("2925.00"),
            cost_gold_dragons=Decimal("5557500.00")
        )

        url = reverse("profile-cost-overview", kwargs={"pk": profile.id})
        response = api_client.get(url, {
            "start_date": "2025-10-01",
            "end_date": "2025-10-02"
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["summary"]["total_feet_built"] == "25.00"
        assert data["summary"]["total_ice_cubic_yards"] == "4875.00"
        assert data["summary"]["total_cost_gold_dragons"] == "9262500.00"
        assert len(data["daily_breakdown"]) == 2

    def test_cost_overview_requires_date_parameters(self, api_client):
        """Should return 400 if date parameters missing."""
        profile = ProfileFactory()
        url = reverse("profile-cost-overview", kwargs={"pk": profile.id})

        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
```

---

## End-to-End Tests

```python
# tests/e2e/test_workflows.py
import pytest
from decimal import Decimal
from datetime import date
from rest_framework import status
from django.urls import reverse

@pytest.mark.e2e
@pytest.mark.django_db
class TestFullConstructionWorkflow:
    """Test complete user workflow from profile creation to analytics."""

    def test_complete_workflow(self, api_client):
        """
        Complete workflow:
        1. Create profile
        2. Create wall section
        3. Record daily progress (3 days)
        4. Query cost overview
        5. Query daily ice usage
        """

        # Step 1: Create profile
        profile_url = reverse("profile-list")
        profile_payload = {
            "name": "Northern Watch",
            "team_lead": "Jon Snow",
            "is_active": True
        }
        response = api_client.post(profile_url, profile_payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        profile_id = response.json()["id"]

        # Step 2: Create wall section (assume endpoint exists)
        section_payload = {
            "section_name": "Tower 1-2",
            "start_position": "0.00",
            "target_length_feet": "500.00"
        }
        # ... create section via API

        # Step 3: Record progress for 3 days
        progress_url = reverse("profile-progress", kwargs={"pk": profile_id})

        for day in [1, 2, 3]:
            payload = {
                "wall_section_id": 1,  # Assuming ID 1
                "date": f"2025-10-{day:02d}",
                "feet_built": str(Decimal("10.00") + Decimal(day)),
                "notes": f"Day {day} progress"
            }
            response = api_client.post(progress_url, payload, format="json")
            assert response.status_code == status.HTTP_201_CREATED

        # Step 4: Query cost overview
        overview_url = reverse("profile-cost-overview", kwargs={"pk": profile_id})
        response = api_client.get(overview_url, {
            "start_date": "2025-10-01",
            "end_date": "2025-10-03"
        })

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["summary"]["total_days"] == 3
        assert Decimal(data["summary"]["total_feet_built"]) > Decimal("30.00")

        # Step 5: Query daily ice usage
        ice_url = reverse("profile-daily-ice-usage", kwargs={"pk": profile_id})
        response = api_client.get(ice_url, {"date": "2025-10-02"})

        assert response.status_code == status.HTTP_200_OK
        assert "total_ice_cubic_yards" in response.json()
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test class
pytest tests/unit/test_models.py::TestProfileModel

# Run specific test function
pytest tests/unit/test_models.py::TestProfileModel::test_create_profile_with_valid_data

# Run tests by marker
pytest -m unit        # Only unit tests
pytest -m integration # Only integration tests
pytest -m "not slow"  # Skip slow tests

# Run with coverage
pytest --cov=apps --cov-report=html

# Run in parallel (faster)
pytest -n auto

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Re-run only failed tests
pytest --lf
```

### CI/CD Pipeline

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          pytest --cov=apps --cov-report=xml -n auto

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Best Practices

### Arrange-Act-Assert Pattern

```python
def test_calculate_ice_usage():
    # Arrange: Set up test data
    calculator = IceUsageCalculator()
    feet_built = Decimal("10.00")

    # Act: Execute the code under test
    result = calculator.calculate_ice_usage(feet_built)

    # Assert: Verify the result
    expected = Decimal("1950.00")
    assert result == expected
```

### Descriptive Test Names

```python
# Good
def test_create_profile_with_duplicate_name_returns_400():
    ...

# Bad
def test_profile_creation():
    ...
```

### One Assertion Per Test (Generally)

```python
# Good - focused test
def test_profile_has_name():
    profile = ProfileFactory(name="Test")
    assert profile.name == "Test"

def test_profile_has_team_lead():
    profile = ProfileFactory(team_lead="Jon")
    assert profile.team_lead == "Jon"

# Acceptable - related assertions
def test_create_profile_returns_complete_data():
    profile = ProfileFactory(name="Test", team_lead="Jon")
    assert profile.name == "Test"
    assert profile.team_lead == "Jon"
    assert profile.is_active is True
```

### Test Isolation

```python
# Each test should be independent
@pytest.mark.django_db
def test_one():
    profile = ProfileFactory()
    assert profile.is_active

@pytest.mark.django_db
def test_two():
    # Database is reset between tests
    assert Profile.objects.count() == 0  # Fresh DB
```

### Use Fixtures for Reusable Setup

```python
@pytest.fixture
def profile_with_sections():
    """Profile with 3 wall sections."""
    profile = ProfileFactory()
    sections = WallSectionFactory.create_batch(3, profile=profile)
    return profile, sections

def test_profile_has_sections(profile_with_sections):
    profile, sections = profile_with_sections
    assert profile.wall_sections.count() == 3
```

---

## Coverage Requirements

### Minimum Coverage: 90%

```bash
# Check coverage
pytest --cov=apps --cov-report=term-missing

# Fail if below threshold
pytest --cov=apps --cov-fail-under=90
```

### What to Test

✅ **Test**:
- Business logic (calculations, validations)
- API endpoints (status codes, response data)
- Model methods and properties
- Service layer functions
- Repository queries

❌ **Don't Test**:
- Django's built-in functionality
- Third-party libraries
- Simple getters/setters
- Auto-generated admin code

---

## TDD Workflow Example

### Feature: Add Profile Deactivation

**Step 1: Write Failing Test**
```python
def test_deactivate_profile_sets_is_active_false():
    profile = ProfileFactory(is_active=True)
    profile.deactivate()
    assert profile.is_active is False
```

**Run**: `pytest tests/unit/test_models.py::test_deactivate_profile_sets_is_active_false`
**Result**: ❌ FAIL (AttributeError: 'Profile' object has no attribute 'deactivate')

**Step 2: Minimal Implementation**
```python
class Profile(models.Model):
    # ... existing fields

    def deactivate(self):
        self.is_active = False
        self.save()
```

**Run**: `pytest tests/unit/test_models.py::test_deactivate_profile_sets_is_active_false`
**Result**: ✅ PASS

**Step 3: Refactor (if needed)**
```python
# Add additional test for edge case
def test_deactivate_already_inactive_profile_is_idempotent():
    profile = ProfileFactory(is_active=False)
    profile.deactivate()
    assert profile.is_active is False  # No error
```

**Step 4: Add API Test**
```python
def test_deactivate_profile_via_api(api_client):
    profile = ProfileFactory(is_active=True)
    url = reverse("profile-deactivate", kwargs={"pk": profile.id})
    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    profile.refresh_from_db()
    assert profile.is_active is False
```

---

## Summary

This TDD specification provides:

✅ **Complete test stack**: pytest + factory_boy + Faker
✅ **Test structure**: Unit, integration, E2E tests
✅ **Code examples**: Models, services, repositories, API
✅ **Best practices**: AAA pattern, descriptive names, isolation
✅ **CI/CD ready**: Parallel execution, coverage reporting
✅ **TDD workflow**: Red-Green-Refactor cycle

**Philosophy**: Every line of production code has a test that drove its creation.
