"""posts/serializers.py"""

from rest_framework import serializers

from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "image",
            "image_url",
            "author",
            "author_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "author_username", "created_at", "updated_at", "image_url"]
        extra_kwargs = {
            "image": {"write_only": True, "required": False},
        }

    def get_image_url(self, obj):
        """Return absolute URL for the image, or null if no image."""
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
