from datetime import date

import pytest
from blog.models import Post


@pytest.fixture(autouse=True)
def configure_mail_settings(settings):
    settings.DEFAULT_FROM_EMAIL = "noreply@example.com"
    settings.NOTIFY_EMAIL = "notify@example.com"


@pytest.fixture
def seeded_post(db):
    return Post.objects.create(
        status=Post.ArticleStatus.PUBLISHED,
        title="Selenium Seed Post",
        date=date.today(),
        content="This post exists to support selenium navigation checks.",
        slug="selenium-seed-post",
    )
