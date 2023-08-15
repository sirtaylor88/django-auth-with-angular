import factory
import pytest
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from pytest_factoryboy import register
from rest_framework.test import APIClient

User = get_user_model()
DEFAULT_PASSWORD = "secretpassword"


@pytest.fixture(name="user")
def build_user(user_factory):
    """Return an user"""

    return user_factory(username="tai")


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture(name="client_log")
def build_client_and_login(user):
    """Create an user and login"""

    client = APIClient()
    client.force_authenticate(user)
    return client


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user_{n}@gmail.com")

    @factory.post_generation
    def set_password(obj, create, extracted, **kwargs):
        obj.set_password(DEFAULT_PASSWORD)
        obj.save()


register(UserFactory)
