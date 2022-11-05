"""
Django settings for explorer project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import logging
import os

import simplejson as json
import urllib3

urllib3.disable_warnings()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "changeme"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "off") == "on"

INTERNAL_IPS = json.loads(os.environ.get("DEBUG_TOOLBAR_INTERNAL_IPS", "[]"))

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True

AUTH_USER_MODEL = "cabinet.User"

# Application definition

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "django_filters",
    "rest_framework",
]

if DEBUG:
    THIRD_PARTY_APPS += ["debug_toolbar", "django_query_profiler"]

LOCAL_APPS = [
    "cabinet",
    "scan",
    "java_wallet",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    MIDDLEWARE += ["django_cprofile_middleware.middleware.ProfilerMiddleware"]
    DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False

    from django_query_profiler.settings import *
    MIDDLEWARE += ["django_query_profiler.client.middleware.QueryProfilerMiddleware"]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "scan.context_processors.settings_context_processor",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_DEFAULT_ENGINE"),
        "NAME": os.environ.get("DB_DEFAULT_NAME"),
        "HOST": os.environ.get("DB_DEFAULT_HOST"),
        "USER": os.environ.get("DB_DEFAULT_USER"),
        "PASSWORD": os.environ.get("DB_DEFAULT_PASSWORD"),
        "OPTIONS": json.loads(os.environ.get("DB_DEFAULT_OPTIONS", "{}")),
    },
    "java_wallet": {
        "ENGINE": os.environ.get("DB_JAVA_WALLET_ENGINE"),
        "NAME": os.environ.get("DB_JAVA_WALLET_NAME"),
        "HOST": os.environ.get("DB_JAVA_WALLET_HOST"),
        "USER": os.environ.get("DB_JAVA_WALLET_USER"),
        "PASSWORD": os.environ.get("DB_JAVA_WALLET_PASSWORD"),
        "OPTIONS": json.loads(os.environ.get("DB_JAVA_WALLET_OPTIONS", "{}")),
    },
}

DATABASE_ROUTERS = ["java_wallet.db_router.DBRouter", "scan.db_router.DBRouter"]


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'redis://{os.environ.get("CACHE_DEFAULT_HOST")}:'
        f'{os.environ.get("CACHE_DEFAULT_PORT")}/'
        f'{os.environ.get("CACHE_DEFAULT_DB")}',
        "TIMEOUT": None,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 25,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "WARNING", "handlers": ["console"]},
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "scan": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# Celery

CELERY_BROKER_URL = (
    f'redis://{os.environ.get("CELERY_BROKER_HOST")}:'
    f'{os.environ.get("CELERY_BROKER_PORT")}/'
    f'{os.environ.get("CELERY_BROKER_DB")}'
)
CELERY_RESULT_BACKEND = None
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERYD_TASK_TIME_LIMIT = 600

# Sentry

SENTRY_DSN = os.environ.get("SENTRY_DSN")

if SENTRY_DSN:
    from sentry_sdk import init
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            LoggingIntegration(event_level=logging.WARNING),
            RedisIntegration(),
        ],
    )

# UA-XXXXXXXXX-X
GOOGLE_TRACKING_ID = os.environ.get("GOOGLE_TRACKING_ID")

DEFAULT_P2P_PORT = int(os.environ.get("DEFAULT_P2P_PORT", 8123))
DEFAULT_API_V1_PORT = int(os.environ.get("DEFAULT_API_V1_PORT", 8125))

BRS_P2P_VERSION = os.environ.get("BRS_P2P_VERSION", "3.2.1")
MIN_PEER_VERSION = os.environ.get("MIN_PEER_VERSION", "3.2.0")

SIGNUM_NODE = os.environ.get("SIGNUM_NODE")

BLOCK_REWARD_LIMIT_HEIGHT = 972000
BLOCK_REWARD_LIMIT_AMOUNT = 100

WALLET_URL = os.environ.get("WALLET_URL")

FEATURED_ASSETS = json.loads(os.environ.get("FEATURED_ASSETS", "[]"))

BLOCKED_ASSETS = json.loads(os.environ.get("BLOCKED_ASSETS", "[]"))
PHISHING_ASSETS = json.loads(os.environ.get("PHISHING_ASSETS", "[]"))

BRS_BOOTSTRAP_PEERS = json.loads(os.environ.get("BRS_BOOTSTRAP_PEERS", "[]"))

PEERS_SCAN_DELAY = int(os.environ.get("PEERS_SCAN_DELAY", "0"))

SITE_HOSTING = os.environ.get("SITE_HOSTING", " ")

# for fork solving
AGGR_STORE_BLOCK_SIGNATURE = 3600 * 24 * 7

TEST_NET = os.environ.get("TEST_NET")
