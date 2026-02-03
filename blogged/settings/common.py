import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = "blogged.urls"

SECRET_KEY = os.environ.get("SECRET_KEY", "TEST_KEY")

INSTALLED_APPS = [
    "dal",  # must be imported before contrib.admin
    "dal_select2",  # must be imported before contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "polymorphic",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic", # equivalent to `dm runserver --nostatic`
    "django.contrib.staticfiles",
    "django_extensions",
    "imagekit",
    "taggit",
    # 'formset',  # https://django-formset.fly.dev/
    "django_flatpickr",  # TODO - do we want to keep this?
    "storages",
    "blog",
    "blogcontact",
    "impact_maps",
    "rest_framework",
    "hitcount",
    "landing_page",
    "activities",
    # 'gdstorage',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "theme.context_processors.theme",
            ],
        },
    },
]

STATIC_URL = "/static/"  # used by django/the app as an api for static files
STATIC_ROOT = BASE_DIR / "staticfiles"  # where collectstatic puts static files for production
STATICFILES_DIRS = [
    BASE_DIR / "static",  # where generic static files are stored - e.g. css, js, images
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# email settings
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL")
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# django-taggit settings
TAGGIT_CASE_INSENSITIVE = True