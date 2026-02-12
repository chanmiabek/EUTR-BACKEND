from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'created_at', 'author', 'author_name']
        read_only_fields = ['author', 'created_at']
