"""Test settings for Wall Construction API."""

from __future__ import annotations

from config.settings.base import (
    ALLOWED_HOSTS,
    BASE_DIR,
    DEFAULT_AUTO_FIELD,
    INSTALLED_APPS,
    LANGUAGE_CODE,
    MIDDLEWARE,
    REST_FRAMEWORK,
    ROOT_URLCONF,
    SECRET_KEY,
    STATIC_URL,
    TEMPLATES,
    TIME_ZONE,
    USE_I18N,
    USE_TZ,
    WORKER_POOL_SIZE,
    WSGI_APPLICATION,
)

__all__ = [
    "ALLOWED_HOSTS",
    "BASE_DIR",
    "DATABASES",
    "DEBUG",
    "DEFAULT_AUTO_FIELD",
    "INSTALLED_APPS",
    "LANGUAGE_CODE",
    "MIDDLEWARE",
    "PASSWORD_HASHERS",
    "REST_FRAMEWORK",
    "ROOT_URLCONF",
    "SECRET_KEY",
    "STATIC_URL",
    "TEMPLATES",
    "TESTING",
    "TIME_ZONE",
    "USE_I18N",
    "USE_TZ",
    "WORKER_POOL_SIZE",
    "WSGI_APPLICATION",
]

DEBUG = False

# Flag to indicate test environment (disables threading for SQLite compatibility)
TESTING = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
