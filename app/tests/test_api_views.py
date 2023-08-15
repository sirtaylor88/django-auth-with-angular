from http import HTTPStatus

import pytest
from django.core import mail
from django.urls import reverse

from app.core import models


@pytest.mark.django_db
def test_register_view(client):
    """Test that RegisterAPIView works correctly."""
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "test@gmail.com",
        "password": "HACKMENOW",
        "password_confirm": "HACKMENOW",
    }
    response = client.post(reverse("register"), payload)

    assert response.status_code == HTTPStatus.OK
    assert models.User.objects.filter(email="test@gmail.com").exists()


@pytest.mark.django_db
def test_login_view(client, user):
    """Test that LoginAPIView works correctly."""
    payload = {
        "email": user.email,
        "password": "secretpassword",
    }
    response = client.post(reverse("login"), payload)

    assert response.status_code == HTTPStatus.OK
    assert "token" in response.data
    assert user.usertoken_set.count() == 1
    assert "refresh_token" in response.client.cookies


@pytest.mark.django_db
def test_user_detail_view(client_log):
    """Test that UserAPIView works correctly."""
    response = client_log.get(reverse("user-detail"))

    assert response.status_code == HTTPStatus.OK
    assert "id" in response.data
    assert "email" in response.data


@pytest.mark.django_db
def test_forgot_view(client):
    """Test that ForgotAPIView works correctly."""
    payload = {"email": "recover_pass@gmail.com"}

    response = client.post(reverse("forgot"), payload)
    assert response.status_code == HTTPStatus.OK
    assert models.Reset.objects.count() == 1
    assert len(mail.outbox) == 1
