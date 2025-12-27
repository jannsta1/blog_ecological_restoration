from rest_framework import serializers
from .models import Post


class BlogPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('pk', 'id', 'title', 'slug', 'date', 'content', 'activities_tag', 'organisation_tags')