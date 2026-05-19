from django.urls import path
from post_operations.views import PostPutView, PostPatchView, PostDeleteView

urlpatterns = [
    path('<int:pk>/put/', PostPutView.as_view(), name='post-put'),
    path('<int:pk>/patch/', PostPatchView.as_view(), name='post-patch'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
]
