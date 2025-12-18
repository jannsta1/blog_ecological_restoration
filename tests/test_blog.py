import pytest
from django.test import Client

from blogged.blog.models import Post
from blogged.blog.forms import PostForm
from datetime import datetime


# @pytest.fixture
# def client():
#     return Client()


@pytest.fixture
def authenticated_client(client, django_user_model):
    username = "testuser"
    password = "testpassword"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client

# @pytest.fixture
# def blog_post():

#     post = Post.objects.create(
#         title="Sample Blog Post",
#         date=datetime.today().date(),
#         content="This is a sample blog post for testing.",
#         slug="sample-blog-post"
#         )
#     return post

# @pytest.fixture
# def blog_form(blog_post):

#     return PostForm()

# @pytest.mark.django_db 
# def test_test(sample_blog_post):
#     assert True
@pytest.mark.django_db
# def test_blog_post_creation(blog_post):
def test_blog_post_creation():

    blog_post = Post.objects.create(
        title="Sample Blog Post",
        date=datetime.today().date(),
        content="This is a sample blog post for testing.",
        slug="sample-blog-post"
        )
    # return post

    assert blog_post.title == "Sample Blog Post"
    assert blog_post.content == "This is a sample blog post for testing."

