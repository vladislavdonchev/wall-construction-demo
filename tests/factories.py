"""Factory definitions for test data generation."""

from __future__ import annotations

from typing import Any

from factory.django import DjangoModelFactory


class BaseFactory(DjangoModelFactory[Any]):
    """Base factory with common configuration."""

    class Meta:
        abstract = True
