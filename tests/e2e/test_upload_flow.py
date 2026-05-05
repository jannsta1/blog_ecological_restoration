import pytest

from tests.e2e.page_objects.upload_post_page import UploadPostPage


@pytest.mark.selenium
@pytest.mark.django_db(transaction=True)
def test_upload_requires_login(selenium_driver, live_server_url):
    upload_page = UploadPostPage(selenium_driver, live_server_url)

    upload_page.open()

    assert "/login/" in selenium_driver.current_url


# @pytest.mark.selenium
# @pytest.mark.django_db(transaction=True)
# def test_authenticated_upload_post_success(
#     selenium_driver,
#     live_server_url,
#     authenticated_user,
# ):
#     login_page = LoginPage(selenium_driver, live_server_url)
#     upload_page = UploadPostPage(selenium_driver, live_server_url)

#     login_page.open()
#     login_page.login(authenticated_user.username, 'selenium_password_123')

#     upload_page.open()
#     upload_page.fill_required_fields(
#         title='E2E Upload Post',
#         date=str(date.today()),
#         content='Selenium test content for upload flow.',
#     )
#     upload_page.add_gps_row(latitude='51.5007', longitude='-0.1246', altitude='10')
#     upload_page.submit()

#     assert '/upload-post/' in selenium_driver.current_url
#     assert 'Post succesfully added' in selenium_driver.page_source
