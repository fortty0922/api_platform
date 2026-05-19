"""posts/urls.py"""

from django.urls import path
from posts.views import PostListCreateView, PostRetrieveView

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:pk>/", PostRetrieveView.as_view(), name="post-retrieve"),
]
