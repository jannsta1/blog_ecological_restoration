import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "blogged"

# ROOT_URLCONF = "spice_orgs.tests.urls"
SECRET_KEY = os.environ.get("SECRET_KEY", "TEST_KEY")
INSTALLED_APPS = [
    'dal', # must be imported before contrib.admin
    'dal_select2', # must be imported before contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 'formset',  # https://django-formset.fly.dev/
    "django_flatpickr",
    "storages",
    "blog",
    "blogcontact",
    "impact_maps",
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

ROOT_URLCONF = "blogged.urls"

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
            ],
        },
    },
]

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]