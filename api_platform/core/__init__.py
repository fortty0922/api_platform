"""
core/authentication.py

Simple UID-based authentication.
Clients pass their user ID in the X-UID header.
The server looks up the User by pk and attaches it to request.user.
"""

from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class UIDAuthentication(BaseAuthentication):
    """
    Authenticate by reading X-UID from the request header.

    Header format:
        X-UID: 3

    Returns the matching User object, or raises AuthenticationFailed.
    Returns None (unauthenticated) if the header is absent — allowing
    public endpoints (e.g. register, list posts) to pass through.
    """

    def authenticate(self, request):
        uid = request.headers.get("X-UID")

        if uid is None:
            # No header → anonymous request; let permission classes decide
            return None

        try:
            uid_int = int(uid)
        except (ValueError, TypeError):
            raise AuthenticationFailed("X-UID must be a valid integer.")

        try:
            user = User.objects.get(pk=uid_int)
        except User.DoesNotExist:
            raise AuthenticationFailed(f"No user found with uid={uid_int}.")

        return (user, None)

    def authenticate_header(self, request):
        return "X-UID"
