from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extend Django User with new attributes."""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class UserToken(models.Model):
    """JSON Web Token belonging to an User"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()


class Reset(models.Model):
    """Reset password request."""

    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
