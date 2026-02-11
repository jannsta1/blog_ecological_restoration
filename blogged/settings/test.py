from settings.common import *  # noqa: F403

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
