import random
import string

import pyotp
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from app.core import models, serializers
from app.core.authentication import JWTAuthentication, create_token, decode_token


def _confirm_password(data):
    if data["password"] != data["password_confirm"]:
        raise exceptions.APIException("Passwords do not match!")


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data
        _confirm_password(data)

        serializer = serializers.UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = models.User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            raise exceptions.AuthenticationFailed("Invalid credentials")

        if user.tfa_secret:
            return Response({"id": user.id})

        secret = pyotp.random_base32()
        otp_auth_url = pyotp.totp.TOTP(secret).provisioning_uri(issuer_name="My App")

        return Response({"id": user.id, "secret": secret, "otp_auth_url": otp_auth_url})


class TwoFactorAPIView(APIView):
    def post(self, request):
        id = request.data["id"]
        user = models.User.objects.filter(pk=id).first()
        if not user:
            raise exceptions.AuthenticationFailed("Invalid credentials")

        secret = user.tfa_secret if user.tfa_secret != "" else request.data["secret"]
        if not pyotp.TOTP(secret).verify(request.data["code"]):
            raise exceptions.AuthenticationFailed("Invalid credentials")

        if user.tfa_secret == "":
            user.tfa_secret = secret
            user.save(update_fields=["tfa_secret"])

        start_date = timezone.now()
        access_token = create_token(
            id,
            "access_secret",
            "HS256",
            start_date=start_date,
            duration_dict={"seconds": 30},
        )
        refresh_token = create_token(
            id,
            "refresh_secret",
            "HS256",
            start_date=start_date,
            duration_dict={"days": 7},
        )

        # Save the refresh token to DB to allow to refresh the page
        # without the need to re-login
        models.UserToken.objects.create(
            user=user,
            token=refresh_token,
            expired_at=start_date + timezone.timedelta(days=7),
        )

        response = Response()
        # Set httponly so only the backend can receive the cookie
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        response.data = {
            "token": access_token,
        }

        return response


class UserAPIView(APIView):
    """View to return user data if authenticated"""

    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response(serializers.UserSerializer(request.user).data)


class RefreshAPIView(APIView):
    """View to create a new access token using user ID decoded from refresh token."""

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        id = decode_token(refresh_token, "refresh_secret", ["HS256"])
        if not models.UserToken.objects.filter(
            user__pk=id, token=refresh_token, expired_date__gte=timezone.now()
        ).exists():
            raise exceptions.AuthenticationFailed("Unauthenticated.")

        access_token = create_token(
            id, "access_secret", "HS256", duration_dict={"seconds": 30}
        )

        return Response({"token": access_token})


class LogoutAPIView(APIView):
    """View to logout an user."""

    authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        # Delete the refresh token so the user needs to re-login
        models.UserToken.objects.filter(token=refresh_token).delete()

        response = Response()
        response.delete_cookie(key="refresh_token")
        response.data = {"message": "success"}

        return response


class ForgotAPIView(APIView):
    """View to request to reset the password."""

    def post(self, request):
        email = request.data["email"]
        token = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(10)
        )
        models.Reset.objects.create(email=email, token=token)

        url = f"http://localhost:3000/reset/{token}"

        send_mail(
            subject="Reset your password!",
            message=f'Click <a href="{url}">here</a> to reset your password.',
            from_email="noreply@example.com",
            recipient_list=[email],
        )

        return Response({"message": "success"})


class ResetAPIView(APIView):
    """View to reset forgotten password."""

    def post(self, request):
        data = request.data
        _confirm_password(data)

        reset_password = models.Reset.objects.filter(token=data["token"]).first()

        if not reset_password:
            raise exceptions.APIException("Invalid link!")

        user = models.User.objects.filter(email=reset_password.email).first()

        if not user:
            raise exceptions.APIException("User not found!")

        user.set_password(data["password"])
        user.save()

        return Response({"message": "success"})
