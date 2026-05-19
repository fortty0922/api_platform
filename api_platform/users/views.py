"""users/views.py"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegisterSerializer


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
