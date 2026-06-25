"""
Django settings for config project.
"""

import os
from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost",
).split(",")

CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core",
    "django_extensions",
    "django_celery_beat",
    "django_ratelimit",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv(
            "REDIS_CACHE_URL",
            "redis://127.0.0.1:6379/1",
        ),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "newsletter@example.com",
)

TEST_RECIPIENT_EMAIL = os.getenv(
    "TEST_RECIPIENT_EMAIL",
    "",
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SEND_REAL_EMAILS = os.getenv("SEND_REAL_EMAILS", "False") == "True"

MAX_EMAILS_PER_DAY = int(
    os.getenv("MAX_EMAILS_PER_DAY", "300")
)

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0",
)

CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/0",
)

CELERY_TIMEZONE = "America/Toronto"

EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp")

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s "
                "[%(levelname)s] "
                "%(name)s: "
                "%(message)s"
            ),
        },
    },

    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/newsletter_agent.log",
            "formatter": "standard",
        },
    },

    "root": {
        "handlers": ["file"],
        "level": "INFO",
    },
}
RATELIMIT_ENABLE = "pytest" not in sys.argv

EMAIL_SEND_DELAY_SECONDS = int(
    os.getenv("EMAIL_SEND_DELAY_SECONDS", "30")
)

SITE_URL = os.getenv(
    "SITE_URL",
    "http://127.0.0.1:8000",
)