from settings.base import *

# -----------------------------------------------------------------------------
# --- Override Settings here
DEBUG = True
DEBUG_TOOLBAR = True

ADMINS = (
    ("Artem Suvorov", "artem.suvorov@gmail.com"),
)

DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.mysql",
        "NAME":     "saneside_dev",
        "USER":     "root",
        "PASSWORD": "root",
        "HOST":     "localhost",
        "PORT":     "3306",
        "OPTIONS": {
            # "autocommit": True,
        }
    }
}

SECURE_SSL_REDIRECT = False


###############################################################################
### DJANGO MIDDLEWARE CLASSES                                               ###
###############################################################################
MIDDLEWARE_CLASSES = (
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "debug_toolbar.middleware.DebugToolbarMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)


###############################################################################
### DJANGO CACHING                                                          ###
###############################################################################
"""
CACHES = {
    "default": {
        "BACKEND":  "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        "TIMEOUT":  60,
    }
}

CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = ""
"""


###############################################################################
### DJANGO LOGGING                                                          ###
###############################################################################
LOGGING = {
    "version":                      1,
    "disable_existing_loggers":     False,
    "filters": {
        "require_debug_false": {
            "()":                   "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()":                   "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "simple": {
            "format":               "[%(asctime)s] %(levelname)s %(message)s",
            "datefmt":              "%Y-%m-%d %H:%M:%S",
        },
        "verbose": {
            "format":               "[%(asctime)s] %(levelname)s "
                                    "[%(name)s.%(funcName)s:%(lineno)d] "
                                    "%(message)s",
            "datefmt":              "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level":                "INFO",
            "filters": [
                "require_debug_true",
            ],
            "class":                "logging.StreamHandler",
            "formatter":            "simple",
        },
        "null": {
            "class":                "logging.NullHandler",
        },
        "mail_admins": {
            "level":                "ERROR",
            "filters": [
                "require_debug_false",
            ],
            "class":                "django.utils.log.AdminEmailHandler",
            "formatter":            "verbose",
        },
        "saneside_logfile": {
            "level":                "DEBUG",
            "filters": [
                "require_debug_true",
            ],
            "class":                "logging.handlers.RotatingFileHandler",
            "filename":             "saneside.log",
            "maxBytes":             1024 * 1024 * 5,  # 5 MB
            "backupCount":          7,
            "formatter":            "verbose",
        },
    },
    "loggers": {
        "saneside": {
            "handlers": [
                "console",
                "saneside_logfile",
            ],
        },
        "django": {
            "handlers": [
                "console",
                "saneside_logfile",
            ],
        },
        "django.request": {
            "handlers": [
                "mail_admins",
                "saneside_logfile",
            ],
            "level":                "ERROR",
            "propagate":            False,
        },
        "py.warnings": {
            "handlers": [
                "console",
                "saneside_logfile",
            ],
        },
    },
}


###############################################################################
### DJANGO DEBUG TOOLBAR                                                    ###
###############################################################################
INSTALLED_APPS += (
    "debug_toolbar",
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
]
INTERNAL_IPS = ["127.0.0.1", ]
RESULTS_CACHE_SIZE = 10
SHOW_COLLAPSED = True
SHOW_TOOLBAR_CALLBACK = True
