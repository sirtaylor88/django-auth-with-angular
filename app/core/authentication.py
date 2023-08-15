from datetime import datetime

import jwt
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from app.core import models


class JWTAuthentication(BaseAuthentication):
    """Middleware to return user from JSON Web token."""

    def authenticate(self, request):
        """Overwrite rest_framework method."""

        # Return a list: ["Bearer", access_token]
        auth = get_authorization_header(request).split()

        if not auth or len(auth) != 2:
            raise exceptions.AuthenticationFailed("Unauthenticated.")

        token = auth[1].decode("utf-8")
        id = decode_token(token, "access_secret", ["HS256"])
        user = models.User.objects.filter(pk=id).first()
        return (user, None)


def create_token(
    id: int,
    key: str,
    alg: str,
    start_date: datetime = None,
    duration_dict: dict[str, int] = {},
) -> str:
    """Generate a JSON Web Token"""

    if start_date is None:
        start_date = timezone.now()

    return jwt.encode(
        {
            "user_id": id,
            "exp": start_date + timezone.timedelta(**duration_dict),
            "iat": start_date,
        },
        key,
        algorithm=alg,
    )


def decode_token(token: str, key: str, algs: list[str]) -> int:
    """Decode a JSON Web Token"""

    try:
        payload = jwt.decode(token, key, algorithms=algs)
    except Exception:
        raise exceptions.AuthenticationFailed("unauthenticated")
    else:
        return payload["user_id"]
