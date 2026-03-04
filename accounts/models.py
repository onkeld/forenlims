# accounts/models.py
from __future__ import annotations

from typing import Mapping, Optional

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Manager for CustomUser."""

    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        **extra_fields: Mapping[str, object],
    ) -> CustomUser:
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: Optional[str] = None,
        **extra_fields: Mapping[str, object],
    ) -> CustomUser:
        """Create a superuser with all permissions."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model for Forensic Lab Management."""

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    # Grants access to Django admin
    is_staff = models.BooleanField(default=False)
    # Grants all permissions
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
    ]  # e.g., first_name, last_name if desired

    def __str__(self) -> str:
        return self.email

    class Meta:
        permissions = [
            ('create_customuser', 'Can create users via admin UI'),
            ('edit_customuser', 'Can edit users via admin UI'),
        ]
