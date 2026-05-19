"""posts/models.py"""

from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    author  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title   = models.CharField(max_length=200)
    content = models.TextField()
    image   = models.ImageField(upload_to="posts/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.pk}] {self.title} by {self.author.username}"
