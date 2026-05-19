"""users/serializers.py"""

from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        # Use create_user so the password is properly hashed
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user
