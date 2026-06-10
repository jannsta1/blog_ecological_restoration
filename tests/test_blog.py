from io import BytesIO
from datetime import datetime

import pytest
from blog.forms import ImageFormSet
from activities.models import TransportCar
from blog.forms import PostForm
from blog import views as blog_views
from blog.models import Post
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from PIL.TiffImagePlugin import IFDRational
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
        slug="sample-blog-post",
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
            slug="sample-blog-post",
        )

    def test_long_title_slug_truncation(self):
        long_title = "A" * 100  # 100 characters long
        post = Post.objects.create(
            title=long_title,
            date=datetime.today().date(),
            content="Testing long title slug truncation.",
        )
        assert len(post.slug) <= Post.MAX_SLUG_LENGTH
        assert post.slug == "a" * Post.MAX_SLUG_LENGTH


@pytest.mark.django_db
def test_post_form_valid(post_form_data):
    assert post_form_data.is_valid()


@pytest.mark.django_db
def test_upload_post_view(authenticated_client):
    url = reverse("upload-post")

    pot_data = {
        "title": "Test Post",
        "date": "2024-06-01",
        "content": "This is a test post content.",
        # GPS formset data is required even if no gps coordinates are added. TODO - why not the case for images?
        "gps-TOTAL_FORMS": "1",
        "gps-INITIAL_FORMS": "0",
        "gps-MIN_NUM_FORMS": "0",
        "gps-MAX_NUM_FORMS": "1000",
    }

    # submit the post, and expect a redirect on success
    response = authenticated_client.post(url, pot_data)
    assert response.status_code == 302

    # follow the redirect and check that the new post page loads correctly
    final_reponse = authenticated_client.get(response.url, follow=True)
    assert final_reponse.status_code == 200


@pytest.mark.django_db
def test_upload_post_stage_one_creates_draft(authenticated_client):
    response = authenticated_client.post(
        reverse("upload-post"),
        {
            "stage": "1",
            "title": "Draft title",
            "date": "2024-06-01",
            "gps-TOTAL_FORMS": "0",
            "gps-INITIAL_FORMS": "0",
            "gps-MIN_NUM_FORMS": "0",
            "gps-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    assert "draft=" in response.url

    post = Post.objects.get(title="Draft title")
    assert post.content == ""


@pytest.mark.django_db
def test_upload_post_stage_two_updates_draft(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="",
        slug="draft-title",
    )

    response = authenticated_client.post(
        reverse("upload-post"),
        {
            "stage": "2",
            "draft_id": str(draft.pk),
            "content": "Stage two content",
            "gps-TOTAL_FORMS": "0",
            "gps-INITIAL_FORMS": "0",
            "gps-MIN_NUM_FORMS": "0",
            "gps-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    draft.refresh_from_db()
    assert draft.content == "Stage two content"


@pytest.mark.django_db
def test_upload_post_stage_two_saves_car_transport_details(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="",
        slug="draft-title-transport",
    )

    response = authenticated_client.post(
        reverse("upload-post"),
        {
            "stage": "2",
            "draft_id": str(draft.pk),
            "content": "Stage two content",
            "travel_option": "car",
            "distance": "21.5",
            "carbon_offset": "on",
            "powertrain": "G",
            "passengers": "3",
            "gps-TOTAL_FORMS": "0",
            "gps-INITIAL_FORMS": "0",
            "gps-MIN_NUM_FORMS": "0",
            "gps-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    transport = TransportCar.objects.get(activity__post=draft)
    assert transport.distance == 21.5
    assert transport.carbon_offset is True
    assert transport.powertrain == "G"
    assert transport.passengers == 3


@pytest.mark.django_db
def test_upload_post_stage_two_ignores_publish_stage_marker(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="",
        slug="draft-title-stage-two-marker",
    )

    response = authenticated_client.post(
        reverse("upload-post"),
        {
            "stage": "2",
            "publish_stage": "3",
            "draft_id": str(draft.pk),
            "content": "Stage two content",
            "gps-TOTAL_FORMS": "0",
            "gps-INITIAL_FORMS": "0",
            "gps-MIN_NUM_FORMS": "0",
            "gps-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    draft.refresh_from_db()
    assert draft.content == "Stage two content"


@pytest.mark.django_db
def test_upload_post_stage_three_saves_empty_formsets(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="Stage two content",
        slug="draft-title",
    )

    response = authenticated_client.post(
        reverse("upload-post"),
        {
            "stage": "3",
            "draft_id": str(draft.pk),
            "gps-TOTAL_FORMS": "0",
            "gps-INITIAL_FORMS": "0",
            "gps-MIN_NUM_FORMS": "0",
            "gps-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    draft.refresh_from_db()
    assert draft.content == "Stage two content"


@pytest.mark.django_db
def test_upload_post_stage_three_publishes_post(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="Stage two content",
        slug="draft-title",
    )

    response = authenticated_client.post(
        reverse("upload-post"),
        {
            "stage": "3",
            "action": "publish",
            "draft_id": str(draft.pk),
            "gps-TOTAL_FORMS": "0",
            "gps-INITIAL_FORMS": "0",
            "gps-MIN_NUM_FORMS": "0",
            "gps-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    draft.refresh_from_db()
    assert draft.status == Post.ArticleStatus.PUBLISHED


@pytest.mark.django_db
def test_upload_post_publish_uses_publish_stage_marker(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="Stage two content",
        slug="draft-title-publish-marker",
    )

    response = authenticated_client.post(
        reverse("upload-post"),
        {
            "publish_stage": "3",
            "action": "publish",
            "draft_id": str(draft.pk),
            "gps-TOTAL_FORMS": "0",
            "gps-INITIAL_FORMS": "0",
            "gps-MIN_NUM_FORMS": "0",
            "gps-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    draft.refresh_from_db()
    assert draft.status == Post.ArticleStatus.PUBLISHED


@pytest.mark.django_db
def test_extract_gps_coords_handles_ifd_rational_altitude(
    authenticated_client, monkeypatch
):
    monkeypatch.setattr(
        blog_views,
        "get_gps_coordinates_from_meta_data",
        lambda image_path: (55.1234, -3.1234, IFDRational(3, 2)),
    )

    response = authenticated_client.post(
        "/extract-gps-coordinates-script/",
        {
            "image": SimpleUploadedFile(
                "gps.jpg", b"fake-image", content_type="image/jpeg"
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "gps_data_found": True,
        "gps_array": [
            {"lat": 55.1234, "lon": -3.1234, "alt": 1.5, "source_name": "gps.jpg"}
        ],
    }


@pytest.mark.django_db
def test_draft_posts_view_lists_only_drafts(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="",
        slug="draft-title",
    )
    published = Post.objects.create(
        title="Published title",
        date=datetime.today().date(),
        content="Published content",
        slug="published-title",
        status=Post.ArticleStatus.PUBLISHED,
    )

    response = authenticated_client.get(reverse("draft_posts"))

    assert response.status_code == 200
    assert draft.title in response.content.decode()
    assert published.title not in response.content.decode()


@pytest.mark.django_db
def test_publish_post_view_publishes_draft(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="Ready to publish",
        slug="draft-title",
    )

    response = authenticated_client.post(reverse("publish_post", args=[draft.pk]))

    assert response.status_code == 302
    draft.refresh_from_db()
    assert draft.status == Post.ArticleStatus.PUBLISHED


@pytest.mark.django_db
def test_publish_post_redirects_to_stage_one_when_post_details_missing(
    authenticated_client,
):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="Ready to publish",
        slug="draft-title-missing-details",
    )
    Post.objects.filter(pk=draft.pk).update(title="")

    response = authenticated_client.post(reverse("publish_post", args=[draft.pk]))

    assert response.status_code == 302
    assert response.url == f"{reverse('upload-post')}?draft={draft.pk}&stage=1"
    assert [message.message for message in get_messages(response.wsgi_request)] == [
        "Complete the post details step before publishing."
    ]
    draft.refresh_from_db()
    assert draft.status == Post.ArticleStatus.DRAFT


@pytest.mark.django_db
def test_upload_post_stage_three_publish_redirects_to_stage_one_when_details_missing(
    authenticated_client,
):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="Stage two content",
        slug="draft-title-stage-three-missing-details",
    )
    Post.objects.filter(pk=draft.pk).update(title="")

    response = authenticated_client.post(
        reverse("upload-post"),
        {
            "stage": "3",
            "action": "publish",
            "draft_id": str(draft.pk),
            "gps-TOTAL_FORMS": "0",
            "gps-INITIAL_FORMS": "0",
            "gps-MIN_NUM_FORMS": "0",
            "gps-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302
    assert response.url == f"{reverse('upload-post')}?draft={draft.pk}&stage=1"
    assert [message.message for message in get_messages(response.wsgi_request)] == [
        "Complete the post details step before publishing."
    ]
    draft.refresh_from_db()
    assert draft.status == Post.ArticleStatus.DRAFT


def build_test_image_file(name="image.png"):
    image = Image.new("RGB", (1, 1), color="green")
    file_obj = BytesIO()
    image.save(file_obj, format="PNG")
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/png")


@pytest.mark.django_db
def test_image_formset_requires_main_image_when_images_are_present():
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="Stage two content",
        slug="draft-title-image-validation",
    )

    formset = ImageFormSet(
        data={
            "images-TOTAL_FORMS": "1",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
            "images-0-caption": "Caption",
        },
        files={"images-0-image": build_test_image_file()},
        instance=draft,
        prefix="images",
    )

    assert not formset.is_valid()
    assert formset.non_form_errors() == [
        "Select at least one main image before saving or publishing."
    ]


@pytest.mark.django_db
def test_delete_draft_view_deletes_draft(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="Ready to delete",
        slug="draft-title-delete",
    )

    response = authenticated_client.post(reverse("delete_draft", args=[draft.pk]))

    assert response.status_code == 302
    assert not Post.objects.filter(pk=draft.pk).exists()


@pytest.mark.django_db
def test_blog_listing_hides_drafts(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="",
        slug="draft-title",
    )
    published = Post.objects.create(
        title="Published title",
        date=datetime.today().date(),
        content="Published content",
        slug="published-title",
        status=Post.ArticleStatus.PUBLISHED,
    )

    response = authenticated_client.get(reverse("blog_listing"))

    assert response.status_code == 200
    body = response.content.decode()
    assert body.count('data-testid="post-card"') == 1
    assert published.slug in body
    assert draft.slug not in body


@pytest.mark.django_db
def test_draft_detail_is_not_public(authenticated_client):
    draft = Post.objects.create(
        title="Draft title",
        date=datetime.today().date(),
        content="",
        slug="draft-title",
    )

    response = authenticated_client.get(draft.get_absolute_url())

    assert response.status_code == 404
