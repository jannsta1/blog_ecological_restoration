from http import HTTPStatus

import pytest
from blog.views import blog_listing
from django.contrib.sessions.backends.db import SessionStore
from hitcount.models import HitCount
from hitcount.models import UrlHit
from hitcount.views import get_client_ip


@pytest.mark.django_db
def test_smoke_test(rf, admin_user):
    # begin by checking that the database is empty
    assert UrlHit.objects.count() == 0
    assert HitCount.objects.count() == 0

    # test setup
    session_key = "testsessionkey"
    request = rf.get("index")
    ip = get_client_ip(request)
    ss = SessionStore(session_key=session_key)  # required for the hitcount app
    request.session = ss
    request.user = admin_user
    response = blog_listing(request)
    assert response.status_code == HTTPStatus.OK

    # Test the Url Hit
    assert UrlHit.objects.count() == 1
    url_hit = UrlHit.objects.first()
    assert url_hit.hits == 1

    # Test the Hit Count
    assert HitCount.objects.count() == 1
    url_hit_count = HitCount.objects.first()
    assert url_hit_count.ip == ip
    assert url_hit_count.url_hit == url_hit
    assert url_hit_count.session == session_key
    assert url_hit_count.date is not None


@pytest.mark.django_db
def test_get_client_ip(rf, admin_user):
    # TODO
    ...
