import pytest
from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth import HASH_SESSION_KEY
from django.contrib.auth import SESSION_KEY
from selenium.webdriver.common.by import By

from tests.e2e.page_objects.blog_page import BlogPage
from tests.e2e.page_objects.contact_page import ContactPage
from tests.e2e.page_objects.nav_bar import NavBar

pytestmark = pytest.mark.selenium  # Mark all tests in this module as Selenium tests


@pytest.mark.django_db(transaction=True)
def test_nav_go_to_contact(selenium_driver, live_server_url):
    nav = NavBar(selenium_driver, live_server_url)
    contact_page = ContactPage(selenium_driver, live_server_url)

    nav.visit("/")
    nav.go_to_contact()

    assert "/contact/" in selenium_driver.current_url
    assert contact_page.text_of(contact_page.CONTACT_TITLE) == "Contact"


@pytest.mark.django_db(transaction=True)
def test_nav_go_to_login(selenium_driver, live_server_url):
    nav = NavBar(selenium_driver, live_server_url)

    nav.visit("/")
    nav.go_to_login()

    assert "/login/" in selenium_driver.current_url


@pytest.mark.django_db(transaction=True)
def test_nav_go_to_upload_unauthenticated(selenium_driver, live_server_url):
    nav = NavBar(selenium_driver, live_server_url)

    nav.visit("/")

    assert not nav.is_visible(nav.UPLOAD_LINK)


@pytest.mark.django_db(transaction=True)
def test_nav_go_to_upload_authenticated(
    selenium_driver, live_server_url, authenticated_user
):
    nav = NavBar(selenium_driver, live_server_url)

    selenium_driver.get(f"{live_server_url}/")

    session_cookie = settings.SESSION_ENGINE
    session_store = __import__(session_cookie, fromlist=["SessionStore"]).SessionStore()
    session_store[SESSION_KEY] = str(authenticated_user.pk)
    session_store[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session_store[HASH_SESSION_KEY] = authenticated_user.get_session_auth_hash()
    session_store.save()

    selenium_driver.add_cookie(
        {
            "name": settings.SESSION_COOKIE_NAME,
            "value": session_store.session_key,
            "path": "/",
        }
    )

    nav.visit("/")

    assert nav.is_visible(nav.UPLOAD_LINK)

    nav.go_to_upload()

    assert "/upload-post/" in selenium_driver.current_url


@pytest.mark.django_db(transaction=True)
def test_blog_listing_and_detail_navigation(
    selenium_driver, live_server_url, seeded_post
):
    del seeded_post
    nav = NavBar(selenium_driver, live_server_url)
    blog_page = BlogPage(selenium_driver, live_server_url)

    nav.visit("/")
    nav.go_to_blog_listing()

    assert blog_page.text_of(blog_page.PAGE_TITLE) == "Blog Posts"
    assert blog_page.post_count() >= 1

    blog_page.open_first_post()
    detail_title = blog_page.text_of((By.CSS_SELECTOR, '[data-testid="detail-title"]'))
    assert "Selenium Seed Post" in detail_title


#
# @pytest.mark.django_db(transaction=True)
# def test_contact_form_submission_success(selenium_driver, live_server_url):
#     contact_page = ContactPage(selenium_driver, live_server_url)

#     contact_page.open()
#     contact_page.submit(
#         email='user@example.com',
#         subject='Selenium Contact Test',
#         message='Testing that contact form submission redirects to success.',
#     )

#     assert '/contact/success/' in selenium_driver.current_url
#     assert contact_page.text_of(contact_page.SUCCESS_TITLE) == 'Message successfully sent.'
