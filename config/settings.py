"""
Django settings for config project.
"""

import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Core security settings
# ---------------------------------------------------------------------------

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "fallback-dev-secret-key",
)

DEBUG = os.getenv("DEBUG", "False").lower() == "true"


def get_comma_separated_env(name, default=""):
    """
    Convert a comma-separated environment variable into a clean list.
    """
    return [
        value.strip()
        for value in os.getenv(name, default).split(",")
        if value.strip()
    ]


ALLOWED_HOSTS = get_comma_separated_env(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)

CSRF_TRUSTED_ORIGINS = get_comma_separated_env(
    "CSRF_TRUSTED_ORIGINS",
    "",
)

CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Railway and similar hosting platforms terminate HTTPS at a proxy.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Keep HSTS conservative during the first deployment.
    # Increase this after confirming HTTPS works correctly.
    SECURE_HSTS_SECONDS = int(
        os.getenv("SECURE_HSTS_SECONDS", "3600")
    )
    SECURE_HSTS_INCLUDE_SUBDOMAINS = (
        os.getenv(
            "SECURE_HSTS_INCLUDE_SUBDOMAINS",
            "False",
        ).lower()
        == "true"
    )
    SECURE_HSTS_PRELOAD = (
        os.getenv(
            "SECURE_HSTS_PRELOAD",
            "False",
        ).lower()
        == "true"
    )


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "django_extensions",
    "django_celery_beat",
    "django_ratelimit",

    "core",
]


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Must appear directly after SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------------------------------
# URLs, templates, and WSGI
# ---------------------------------------------------------------------------

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors.request"
                ),
                (
                    "django.contrib.auth.context_processors.auth"
                ),
                (
                    "django.contrib.messages.context_processors.messages"
                ),
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    # Railway and most hosting platforms provide DATABASE_URL.
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=not DEBUG,
        )
    }
else:
    # Local PostgreSQL configuration.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv(
                "DB_NAME",
                "newsletter_agent",
            ),
            "USER": os.getenv(
                "DB_USER",
                "newsletter_user",
            ),
            "PASSWORD": os.getenv(
                "DB_PASSWORD",
                "",
            ),
            "HOST": os.getenv(
                "DB_HOST",
                "localhost",
            ),
            "PORT": os.getenv(
                "DB_PORT",
                "5432",
            ),
        }
    }


# ---------------------------------------------------------------------------
# Cache and rate limiting
# ---------------------------------------------------------------------------

REDIS_CACHE_URL = os.getenv(
    "REDIS_CACHE_URL",
    "",
).strip()

if REDIS_CACHE_URL:
    CACHES = {
        "default": {
            "BACKEND": (
                "django.core.cache.backends.redis.RedisCache"
            ),
            "LOCATION": REDIS_CACHE_URL,
        }
    }
else:
    # Lets the web app run without Redis during the first deployment.
    # This is suitable for a single web process and subscription-page use.
    CACHES = {
        "default": {
            "BACKEND": (
                "django.core.cache.backends.locmem.LocMemCache"
            ),
            "LOCATION": "newsletter-agent-cache",
        }
    }

RATELIMIT_ENABLE = "pytest" not in sys.argv


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ---------------------------------------------------------------------------
# Language and timezone
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Toronto"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# ---------------------------------------------------------------------------
# Uploaded media
# ---------------------------------------------------------------------------

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Note:
# Railway's normal application filesystem is not permanent.
# Add persistent storage before relying on production campaign uploads.


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "",
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587",
    )
)

EMAIL_USE_TLS = (
    os.getenv(
        "EMAIL_USE_TLS",
        "True",
    ).lower()
    == "true"
)

EMAIL_USE_SSL = (
    os.getenv(
        "EMAIL_USE_SSL",
        "False",
    ).lower()
    == "true"
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    "",
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "newsletter@example.com",
)

TEST_RECIPIENT_EMAIL = os.getenv(
    "TEST_RECIPIENT_EMAIL",
    "",
)

EMAIL_PROVIDER = os.getenv(
    "EMAIL_PROVIDER",
    "smtp",
)

SEND_REAL_EMAILS = (
    os.getenv(
        "SEND_REAL_EMAILS",
        "False",
    ).lower()
    == "true"
)

MAX_EMAILS_PER_DAY = int(
    os.getenv(
        "MAX_EMAILS_PER_DAY",
        "300",
    )
)

EMAIL_SEND_DELAY_MIN_SECONDS = int(
    os.getenv(
        "EMAIL_SEND_DELAY_MIN_SECONDS",
        "20",
    )
)

EMAIL_SEND_DELAY_MAX_SECONDS = int(
    os.getenv(
        "EMAIL_SEND_DELAY_MAX_SECONDS",
        "25",
    )
)

if EMAIL_SEND_DELAY_MIN_SECONDS > EMAIL_SEND_DELAY_MAX_SECONDS:
    raise ValueError(
        "EMAIL_SEND_DELAY_MIN_SECONDS cannot be greater than "
        "EMAIL_SEND_DELAY_MAX_SECONDS."
    )


# ---------------------------------------------------------------------------
# Public application address
# ---------------------------------------------------------------------------

SITE_URL = os.getenv(
    "SITE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

COMMUNICATION_PREFERENCES_URL = os.getenv(
    "COMMUNICATION_PREFERENCES_URL",
    "",
)


# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0",
)

CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    CELERY_BROKER_URL,
)

CELERY_TIMEZONE = "America/Toronto"

CELERY_ENABLE_UTC = True

CELERY_TASK_TRACK_STARTED = True

CELERY_TASK_TIME_LIMIT = int(
    os.getenv(
        "CELERY_TASK_TIME_LIMIT",
        "1800",
    )
)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/admin/login/"


# ---------------------------------------------------------------------------
# Model defaults
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

# Console logging works both locally and on Railway.
# Railway captures this output in its deployment logs.
LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

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
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}