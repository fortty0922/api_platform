from rest_framework import permissions
from rest_framework.generics import UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from core.authentication import UIDAuthentication
from posts.models import Post
from posts.serializers import PostSerializer

class IsAuthor(permissions.BasePermission):
    """
    Object-level permission to only allow authors of an object to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class PostPutView(UpdateAPIView):
    """
    PUT /api/operations/posts/<id>/put/
    Fully replace a post.
    """
    http_method_names = ['put']
    serializer_class = PostSerializer
    authentication_classes = [UIDAuthentication]
    permission_classes = [IsAuthenticated, IsAuthor]

    def get_queryset(self):
        return Post.objects.all()


class PostPatchView(UpdateAPIView):
    """
    PATCH /api/operations/posts/<id>/patch/
    Partially update a post.
    """
    http_method_names = ['patch']
    serializer_class = PostSerializer
    authentication_classes = [UIDAuthentication]
    permission_classes = [IsAuthenticated, IsAuthor]

    def get_queryset(self):
        return Post.objects.all()


class PostDeleteView(DestroyAPIView):
    """
    DELETE /api/operations/posts/<id>/delete/
    Delete a post.
    """
    http_method_names = ['delete']
    serializer_class = PostSerializer
    authentication_classes = [UIDAuthentication]
    permission_classes = [IsAuthenticated, IsAuthor]

    def get_queryset(self):
        return Post.objects.all()
