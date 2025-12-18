
import pytest
from blog.views import index

@pytest.mark.asyncio
def test_home(rf, admin_user):
    request = rf.get('index')
    # # Remember that when using RequestFactory, the request does not pass
    # # through middleware. If your view expects fields such as request.user
    # # to be set, you need to set them explicitly.
    # # The following line sets request.user to an admin user.
    request.user = admin_user
    response = index(request)
    assert response.status_code == 200
