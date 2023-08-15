from rest_framework.serializers import ModelSerializer

from app.core.models import User


class UserSerializer(ModelSerializer):
    """Serializer for model User."""

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Overwrite create method to set new password."""

        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()

        return instance
