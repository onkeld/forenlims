# tests/conftest.py
"""Test configuration and fixtures."""

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db: Any) -> None:  # noqa: ANN401
    """Ensures the database is available for all tests."""


@pytest.fixture(autouse=True)
def use_locmem_email_backend(settings) -> None:
    """
    Overwrites the email backend to use the
    in-memory backend for testing.
    """
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
