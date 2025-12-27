from blog.models import Post
from blog.serializers import BlogPostSerializer


from rest_framework.generics import ListAPIView
from rest_framework.response import Response


class PostListAPI(ListAPIView):

    def get(self, request):
        organisation_id = request.GET.get("organisation_id", "all")
        activity_id = request.GET.get("activity_id", "all")

        filtered_posts = Post.objects.all()

        if organisation_id != "all":
            filtered_posts = filtered_posts.filter(organisation_tags__id=organisation_id).distinct()
        if activity_id != "all":
            filtered_posts = filtered_posts.filter(activities_tag__id=activity_id).distinct()

        serializer = BlogPostSerializer(filtered_posts, many=True)
        return Response({"posts": serializer.data})