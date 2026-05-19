"""users/views.py"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegisterSerializer
from django.contrib.auth import authenticate


class RegisterView(APIView):
    """
    POST /api/auth/register/

    Request body:
        { "username": "alice", "password": "Pass1234" }

    Response 201:
        { "uid": 3, "username": "alice" }

    Response 400 (validation error):
        { "username": ["A user with that username already exists."] }
    """

    authentication_classes = []   # no auth required for registration
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response(
            {"uid": user.pk, "username": user.username},
            status=status.HTTP_201_CREATED,
        )

class LoginView(APIView):
    """
    POST /api/auth/login/

    Request body:
        { "username": "alice", "password": "Pass1234" }

    Response 200:
        { "uid": 3, "username": "alice" }

    Response 401 (Invalid credentials):
        { "detail": "Invalid username or password" }
    """

    authentication_classes = []   # no auth required for login
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is not None:
            return Response(
                {"uid": user.pk, "username": user.username},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
