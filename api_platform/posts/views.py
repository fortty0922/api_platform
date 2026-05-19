"""
posts/views.py

GET  /api/posts/     — list all posts (public, paginated)
POST /api/posts/     — create post (requires X-UID)
DELETE /api/posts/<id>/ — delete own post (requires X-UID + author)
"""

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from core.authentication import UIDAuthentication
from posts.models import Post
from posts.serializers import PostSerializer


# ── Pagination ────────────────────────────────────────────────────────────────

class PostPagination(PageNumberPagination):
    """
    Supports ?page=<n>&page_size=<n>.
    Defaults to 10 per page; client can override up to 100.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# ── Views ─────────────────────────────────────────────────────────────────────

class PostListCreateView(ListCreateAPIView):
    """
    GET  /api/posts/?page=1&page_size=10
        — Public. Returns paginated list of all posts (newest first).

    POST /api/posts/
        — Requires X-UID header.
        — Body: { title, content, image? }  (multipart/form-data for image)
    """

    serializer_class = PostSerializer
    authentication_classes = [UIDAuthentication]
    pagination_class = PostPagination
    
    # Filtering and searching
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']  # default ordering

    def get_queryset(self):
        queryset = Post.objects.select_related("author").all()
        # Optional custom filter by author ID
        author_id = self.request.query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveView(RetrieveAPIView):
    """
    GET /api/posts/<id>/
    Publicly retrieve a single post.
    """
    serializer_class = PostSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.select_related("author").all()
