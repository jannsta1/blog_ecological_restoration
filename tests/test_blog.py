import pytest
from django.test import Client
from datetime import datetime
from django.urls import reverse


from blog.models import Post
from blog.forms import PostForm
from blog.views import upload_post
# from blogged.blog.forms import PostForm


@pytest.fixture
def authenticated_client(client, django_user_model):
    username = "testuser"
    password = "testpassword"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client

@pytest.fixture
def blog_post():
    post = Post.objects.create(
        title="Sample Blog Post",
        date=datetime.today().date(),
        content="This is a sample blog post for testing.",
        slug="sample-blog-post"
        )
    return post

@pytest.fixture
def post_form_data(blog_post):
    data = {
        "title": blog_post.title,
        "date": blog_post.date,
        "content": blog_post.content,
        "slug": None,
    }
    form = PostForm(data=data)
    yield form

@pytest.mark.django_db
class TestBlogPostCreation:    
    def test_blog_post_creation(self, blog_post):
        assert blog_post.title == "Sample Blog Post"
        assert blog_post.content == "This is a sample blog post for testing."
        assert blog_post.date == datetime.today().date()
        # check that auto-generated items are set correctly
        assert blog_post.slug == "sample-blog-post"
        # assert blog_post.created_at == datetime.today() # TODO - how to handle the time difference?
        assert blog_post.id is not None  # should be set after save

    def test_duplicates_do_not_raise_error(self, blog_post):
        # create a second blog post with the same slug
        Post.objects.create(
            title="Sample Blog Post",
            date=datetime.today().date(),
            content="This is a sample blog post for testing.",
            slug="sample-blog-post"
        )

    def test_long_title_slug_truncation(self):
        long_title = "A" * 100  # 100 characters long
        post = Post.objects.create(
            title=long_title,
            date=datetime.today().date(),
            content="Testing long title slug truncation."
        )
        assert len(post.slug) <= Post.MAX_SLUG_LENGTH
        assert post.slug == "a" * Post.MAX_SLUG_LENGTH


@pytest.mark.django_db
def test_post_form_valid(post_form_data):
    assert post_form_data.is_valid()


@pytest.mark.django_db
def test_upload_post_view(authenticated_client):

    url = reverse('upload-post')

    pot_data = {
        'title': 'Test Post',
        'date': '2024-06-01',
        'content': 'This is a test post content.',
        # GPS formset data is required even if no gps coordinates are added. TODO - why not the case for images?
        'gps-TOTAL_FORMS': '1',
        'gps-INITIAL_FORMS': '0',
        'gps-MIN_NUM_FORMS': '0',
        'gps-MAX_NUM_FORMS': '1000',
    }
    
    # submit the post, and expect a redirect on success
    response = authenticated_client.post(url, pot_data)
    assert response.status_code == 302 

    # follow the redirect and check that the new post page loads correctly
    final_reponse = authenticated_client.get(response.url, follow=True)
    assert final_reponse.status_code == 200
    