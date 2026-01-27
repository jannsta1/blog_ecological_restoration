from blog.models import Post


def run():
    post = Post.objects.get_or_create(title="Tree Planting Activity at Talla")

    print(post)
