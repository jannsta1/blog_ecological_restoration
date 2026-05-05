# import dotenv
# import django
# def pytest_sessionstart(session):
#     dotenv.load_dotenv(".env.pytest")
#     django.setup()
"""
Pytest configuration and fixtures for the jewelry shop SaaS platform.
"""

from pathlib import Path
import shutil

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=("chrome", "firefox"),
        help="Browser for selenium tests.",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run selenium browser with UI enabled.",
    )
    parser.addoption(
        "--chrome-binary",
        action="store",
        default=None,
        help="Optional explicit path to the Chrome binary.",
    )


@pytest.fixture(scope="function")
def selenium_driver(request, live_server):
    browser = request.config.getoption("--browser")
    headed = request.config.getoption("--headed")

    if browser == "firefox":
        firefox_binary = shutil.which("firefox")
        if firefox_binary is None:
            pytest.skip("Firefox binary was not found in PATH.")

        options = FirefoxOptions()
        options.binary_location = firefox_binary
        if not headed:
            options.add_argument("--headless")
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=options,
        )
    else:
        chrome_binary = (
            request.config.getoption("--chrome-binary")
            or shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
        )
        if chrome_binary is None:
            pytest.skip(
                "Chrome binary was not found. Set --chrome-binary or install Chrome."
            )

        options = ChromeOptions()
        options.binary_location = chrome_binary
        if not headed:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options,
        )

    driver.set_window_size(1440, 900)
    driver.implicitly_wait(0)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def live_server_url(live_server):
    return live_server.url


@pytest.fixture
def authenticated_user(django_user_model):
    return django_user_model.objects.create_user(
        username="selenium_user",
        password="selenium_password_123",
        email="selenium@example.com",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def capture_selenium_artifacts_on_failure(request):
    yield
    if "selenium" not in request.keywords:
        return

    if not hasattr(request.node, "rep_call") or request.node.rep_call.passed:
        return

    if "selenium_driver" not in request.fixturenames:
        return

    driver = request.node.funcargs.get("selenium_driver")
    if driver is None:
        return

    artifacts_dir = Path("test-artifacts/screenshots")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    safe_name = request.node.nodeid.replace("/", "_").replace("::", "__")
    screenshot_path = artifacts_dir / f"{safe_name}.png"
    driver.save_screenshot(str(screenshot_path))


@pytest.fixture
def request_with_session(rf):
    """
    Fixture that provides a RequestFactory request with an attached session.
    This allows testing views that depend on request.session.
    """
    request = rf.get("/")
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    return request


# @pytest.fixture(scope="session")
# def django_db_setup(django_db_blocker):
#     """
#     Configure the test database and verify RLS configuration.

#     IMPORTANT: The tenants table MUST have RLS enabled for proper tenant isolation.
#     Tenants can only see their own record. Platform admins use RLS bypass to see all.
#     """
#     settings.DATABASES["default"] = {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "test_jewelry_shop",
#         "USER": "postgres",
#         "PASSWORD": "postgres",
#         "HOST": "db",  # Docker service name
#         "PORT": "5432",
#         "ATOMIC_REQUESTS": True,
#     }

#     # After database is created, ensure correct RLS configuration
#     # This runs after migrations, so we can verify RLS is properly enabled
#     with django_db_blocker.unblock():
#         from django.db import connection

#         with connection.cursor() as cursor:
#             # Ensure tenants table HAS RLS enabled with FORCE
#             # This is critical for tenant isolation
#             cursor.execute(
#                 """
#                 ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
#                 ALTER TABLE tenants FORCE ROW LEVEL SECURITY;
#             """
#             )

#             # Verify it worked
#             cursor.execute(
#                 """
#                 SELECT relname, relrowsecurity, relforcerowsecurity
#                 FROM pg_class
#                 WHERE relname = 'tenants';
#             """
#             )
#             result = cursor.fetchone()
#             if result:
#                 relname, rls_enabled, rls_forced = result
#                 msg = (
#                     f"RLS not properly enabled on {relname}: rls={rls_enabled}, forced={rls_forced}"
#                 )
#                 assert rls_enabled and rls_forced, msg


# @pytest.fixture
# def authenticated_client(api_client, django_user_model):
#     """
#     Fixture for authenticated API client.
#     """
#     user = django_user_model.objects.create_user(
#         username="testuser", email="test@example.com", password="testpass123"
#     )
#     api_client.force_authenticate(user=user)
#     return api_client, user
