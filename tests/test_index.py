from http import HTTPStatus

import pytest
from blog.views import blog_listing
from django.contrib.sessions.backends.db import SessionStore


@pytest.mark.django_db
def test_home(rf, admin_user):
    request = rf.get("index")

    ss = SessionStore()  # required fot the hitcount app
    request.session = ss
    request.user = admin_user

    response = blog_listing(request)
    assert response.status_code == HTTPStatus.OK  # 200
