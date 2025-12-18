import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ROOT_URLCONF = "spice_orgs.tests.urls"
SECRET_KEY = os.environ.get("SECRET_KEY", "TEST_KEY")
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 'formset',  # https://django-formset.fly.dev/
    "django_flatpickr",
    "storages",
    "blogged",
    # "blogged.blogcontact",
    # "blogged.impact_maps",
    # 'gdstorage',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        # "USER": "",
        # "PASSWORD": "",
        # "HOST": "",
        # "PORT": "",
    }
}