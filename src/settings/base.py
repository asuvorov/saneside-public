from __future__ import absolute_import

import importlib
import os
import os.path
import random
import sys

from django.utils.translation import ugettext_lazy as _

from termcolor import colored, cprint


# -----------------------------------------------------------------------------
# --- PRODUCT VERSIONS
PRODUCT_NAME = "SaneSide Server"
RELEASE_TYPE = {
    "ALPHA":    "alpha",
    "BETA":     "beta",
    "RC":       "rc",
}

# --- Versioning Strategy
#     <major>.<minor>.<patch>[-<type><attempt>]
#     <major>.<minor>.<patch>.<build>[-<type><attempt>]

VERSION_API = 1
VERSION_NAME = "SaneSide"
VERSION_YEAR = 2018
# --- Major version is a number indicating a significant change in the
#     application. A major version might possibly be a complete rewrite of the
#     previous major version and/or break backwards compatibility with older
#     versions.
VERSION_MAJOR = 2
# --- Minor version is a number that indicates a small set of changes from the
#     previous minor version. A minor version usually consists of an even set
#     of bug fixes and new features and should always be backwards compatible.
VERSION_MINOR = 0
# --- Patch is a number that indicates some bugs were fixed that could not wait
#     until the next minor release. A patch version should only include bug
#     fixes and never include new features. It should also always be backwards
#     compatible. Security fixes are an example of a typical patch.
VERSION_PATCH = 2
# --- Build Number is incremented when new build is created.
VERSION_BUILD = 1714
# --- This is last part is optional and only used to identify that this version
#     is not necessarily stable. The type is a keyword and can be anything but
#     usually sticks to "alpha", "beta", and "RC".
#     The attempt is just a number to indicate which attempt at this type is
#     this. So for example, "beta-01", "RC-02", "RC-05", etc. For a stable
#     version, leave off this part, however, other projects like to use the
#     keyword of RELEASE to indicate the stable version.
VERSION_RELEASE = RELEASE_TYPE["BETA"]
VERSION_ATTEMPT = 1

PRODUCT_VERSION_FULL = (
    "{pname}, v.{major}.{minor}.{patch}-{rtype}{atmpt}: {vname}".format(
        pname=PRODUCT_NAME,
        major=VERSION_MAJOR,
        minor=VERSION_MINOR,
        patch=VERSION_PATCH,
        rtype=VERSION_RELEASE,
        atmpt=VERSION_ATTEMPT,
        vname=VERSION_NAME,
    )
)
PRODUCT_VERSION_NUM = (
    "v.{major}.{minor}.{patch}-{rtype}{atmpt}".format(
        major=VERSION_MAJOR,
        minor=VERSION_MINOR,
        patch=VERSION_PATCH,
        rtype=VERSION_RELEASE,
        atmpt=VERSION_ATTEMPT,
    )
)


# -----------------------------------------------------------------------------
# --- SETTINGS
DEBUG = True
DEBUG_TOOLBAR = True

# PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",))
print colored("[---  INFO   ---] PROJECT_PATH           : %s" % PROJECT_PATH, "cyan")

# We have 4 types of environments: "production", "development", "staging"
# and "testing"
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
print colored("[---  INFO   ---] ENVIRONMENT            : %s" % ENVIRONMENT, "cyan")

DJANGO_SETTINGS_MODULE = os.environ.get(
    "DJANGO_SETTINGS_MODULE", "settings.development")
print colored("[---  INFO   ---] DJANGO_SETTINGS_MODULE : %s" % DJANGO_SETTINGS_MODULE, "cyan")

ADMINS = (
    ("Artem Suvorov", "artem.suvorov@gmail.com"),
)
MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.sqlite3",
        "NAME":     "sqlite.db",
        "USER":     "",
        "PASSWORD": "",
        "HOST":     "",
        "PORT":     "",
    }
}

DOMAIN_NAME = "saneside.com"
ALLOWED_HOSTS = ["*"]
APPEND_SLASH = True

TIME_ZONE = "America/Los_Angeles"

LANGUAGE_CODE = "en-us"
LANGUAGES = (
    ("en",  _("English")),
    ("de",  _("Deutsch")),
    ("es",  _("Spanish")),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, "locale"),
)

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

ADMIN_MEDIA_PREFIX = "/static/admin/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, "staticserve")
STATICFILES_DIRS = (
    ("", "%s/static" % PROJECT_PATH),
    )
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.DefaultStorageFinder",
)

SECRET_KEY = "@zew8t_wcz!qn9=8+hheltx@&b#!x@i6ores96lhbnobr3jp*c"
SECURE_SSL_REDIRECT = True

TEMPLATES = [
    {
        "BACKEND":  "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_PATH, "templates/"),
            os.path.join(PROJECT_PATH, "templates/emails/"),
            os.path.join(PROJECT_PATH, "templates/cyborg/"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug":    DEBUG,
            # "loaders": [
            #     "django.template.loaders.filesystem.Loader",
            #     "django.template.loaders.app_directories.Loader",
            # ],
            "context_processors": [
                "django.template.context_processors.csrf",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",

                "url_tools.context_processors.current_url",

                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",

                "accounts.context_processors.signin_form",

                "challenges.context_processors.pb_challenge_choices",
                "challenges.context_processors.pb_participation_choices",
                "challenges.context_processors.pb_recurrence_choices",

                "core.context_processors.pb_settings",
                "core.context_processors.pb_social_links",
                "core.context_processors.pb_social_link_choices",
            ],
        },
    },
]


###############################################################################
### DJANGO MIDDLEWARE CLASSES                                               ###
###############################################################################
MIDDLEWARE_CLASSES = (
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "urls"

WSGI_APPLICATION = "wsgi.application"

INSTALLED_APPS = (
    # --- Django Apps
    "grappelli",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",

    # --- 3rd Party Apps
    "adminsortable2",
    "bootstrap3_datetime",
    "djangosecure",
    "django_countries",
    "jquery",
    "djangoformsetjs",
    "papertrail",
    "rangefilter",
    "sslserver",
    "storages",
    "timezone_field",
    "twitter_tag",
    "url_tools",

    # --- Project Apps
    "accounts",
    "api",
    "app",
    "blog",
    "challenges",
    "core",
    "foro",
    "home",
    "invites",
    "organizations",
    "tests",
)

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"


###############################################################################
### DJANGO CACHING                                                          ###
###############################################################################
CACHES = {
    "default": {
        "BACKEND":  "django.core.cache.backends.dummy.DummyCache",
    }
}


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
    },
    "loggers": {
        "django": {
            "handlers": [
                "console",
            ],
        },
        "django.request": {
            "handlers": [
                "mail_admins",
            ],
            "level":                "ERROR",
            "propagate":            False,
        },
        "py.warnings": {
            "handlers": [
                "console",
            ],
        },
    },
}

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)


###############################################################################
### CUSTOM PROJECT SETTINGS                                                 ###
###############################################################################
SELFREFLECTION_SUBMIT_DURATION_PERIOD = 7  # Days
PROFILE_COMPLETENESS_GRACE_PERIOD = 5  # Days

CHALLENGE_NAME_RESERVED_WORDS = [
    "near-you", "new", "dateless", "featured", "categories",
]
ORGANIZATION_NAME_RESERVED_WORDS = [
    "directory", "create",
]


###############################################################################
### DJANGO BOWER                                                            ###
###############################################################################
INSTALLED_APPS += (
    "djangobower",
)
STATICFILES_FINDERS += (
    "djangobower.finders.BowerFinder",
)

BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_PATH, "components/")
BOWER_PATH = "/usr/local/bin/bower"
BOWER_INSTALLED_APPS = (
    "awesome-bootstrap-checkbox#0.3.7",
    "bootpag",
    "bootstrap#3.3.7",
    "bootstrap-maxlength",
    "bootstrap-rating",
    "bootstrap-select",
    "bootstrap-tabcollapse",
    "bootstrap-tagsinput",
    "bx-slider.js",
    "equalheight",
    "fontawesome",
    "font-awesome-animation",
    "isMobile",
    "isotope",
    "jquery#2.1.4",
    "jquery.inputmask",
    "jquery.pulsate",
    "jquery-colorbox",
    "jquery-file-upload",
    "jquery-popup-overlay",
    "jquery-scrolltotop",
    "jquery-shorten-js",
    "jquery-sticky",
    "jquery-ui",
    "jt.timepicker",
    "less.js",
    "modernizr#2.8.3",  # 3.5.0
    "moment#2.8.4",     # 2.20.1
    "noty",
    "readmore-js",
    "seiyria-bootstrap-slider",
    "smooth-scroll.js",
    "tablesorter",
    "underscore",
    "zabuto_calendar",
)


###############################################################################
### DJANGO CKEDITOR                                                         ###
###############################################################################
INSTALLED_APPS += (
    "ckeditor",
    "ckeditor_uploader",
)

AWS_QUERYSTRING_AUTH = False

CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_RESTRICT_BY_DATE = True
CKEDITOR_RESTRICT_BY_USER = False
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = True

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar":      "full",
        "height":       300,
        "width":        300,
    },
    "awesome_ckeditor": {
        "toolbar_CustomToolbarConfig": [
            {
                "name":     "document",
                "items": [
                    "Source", "-",
                    "Save", "NewPage", "Preview", "Print", "-",
                    "Templates",
                ]
            },
            {
                "name":     "clipboard",
                "items": [
                    "Cut", "Copy", "Paste", "PasteText", "PasteFromWord", "-",
                    "Undo", "Redo",
                ]
            },
            {
                "name":     "editing",
                "items": [
                    "Find", "Replace", "-",
                    "SelectAll",
                ]
            },
            {
                "name":     "forms",
                "items": [
                    "Form", "Checkbox", "Radio", "TextField", "Textarea", "Select", "Button", "ImageButton", "HiddenField",
                ]
            },
            "/",
            {
                "name":     "basicstyles",
                "items": [
                    "Bold", "Italic", "Underline", "Strike", "Subscript", "Superscript", "-",
                    "RemoveFormat",
                ]
            },
            {
                "name":     "paragraph",
                "items": [
                    "NumberedList", "BulletedList", "-",
                    "Outdent", "Indent", "-",
                    "Blockquote", "CreateDiv", "-",
                    "JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock", "-",
                    "BidiLtr", "BidiRtl", "Language",
                ]
            },
            {
                "name":     "links",
                "items": [
                    "Link", "Unlink", "Anchor",
                ]
            },
            {
                "name":     "insert",
                "items": [
                    "Image", "Flash", "Table", "HorizontalRule", "Smiley", "SpecialChar", "PageBreak", "Iframe",
                ]
            },
            "/",
            {
                "name":     "styles",
                "items": [
                    "Styles", "Format", "Font", "FontSize",
                ]
            },
            {
                "name":     "colors",
                "items": [
                    "TextColor", "BGColor",
                ]
            },
            {
                "name":     "tools",
                "items": [
                    "Maximize", "ShowBlocks",
                ]
            },
            {
                "name":     "about",
                "items": [
                    "About",
                ]
            },
        ],
        "toolbar_CustomToolbarSmallConfig": [
            {
                "name":     "document",
                "items": [
                    "Source",
                ]
            },
            {
                "name":     "clipboard",
                "items": [
                    "Undo", "Redo",
                ]
            },
            {
                "name":     "tools",
                "items": [
                    "Maximize", "ShowBlocks", "About",
                ]
            },
            "/",
            {
                "name":     "basicstyles",
                "items": [
                    "Bold", "Italic", "Underline", "Strike", "Subscript", "Superscript", "-",
                    "Outdent", "Indent", "-",
                ]
            },
            {
                "name":     "paragraph",
                "items": [
                    "NumberedList", "BulletedList", "-",
                    "Blockquote", "CreateDiv", "-",
                    "JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock",
                ]
            },
            {
                "name":     "insert",
                "items": [
                    "Link", "Image", "Table", "HorizontalRule", "Smiley", "SpecialChar",
                ]
            },
            "/",
            {
                "name":     "styles",
                "items": [
                    "Styles", "Format", "Font", "FontSize", "TextColor", "BGColor",
                ]
            },
        ],
        "toolbar":      "CustomToolbarSmallConfig",
        # "skin":         "moono",
        "height":       200,
        "width":        "100%",
        "tabSpaces":    4,
    },
}

IMAGE_QUALITY = 60
THUMBNAIL_SIZE = (300, 300)

X_FRAME_OPTIONS = "SAMEORIGIN"


###############################################################################
### DJANGO COMPRESSOR SETTINGS                                              ###
###############################################################################
INSTALLED_APPS += (
    "compressor",
)
STATICFILES_FINDERS += (
    "compressor.finders.CompressorFinder",
)

COMPRESS_PRECOMPILERS = (
    ("text/less", "lessc {infile} {outfile}"),
)

COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]
COMPRESS_JS_FILTERS = [
    "compressor.filters.jsmin.JSMinFilter",
]

COMPRESS_ENABLED = True


###############################################################################
### DJANGO CYBORG                                                           ###
###############################################################################
INSTALLED_APPS += (
    "cyborg",
)


###############################################################################
### DJANGO EASY TIMEZONES                                                   ###
###############################################################################
INSTALLED_APPS += (
    "easy_timezones",
)
MIDDLEWARE_CLASSES += (
    "easy_timezones.middleware.EasyTimezoneMiddleware",
)
GEOIP_DATABASE = os.path.join(PROJECT_PATH, "geoip/GeoLiteCity.dat")
GEOIPV6_DATABASE = os.path.join(PROJECT_PATH, "geoip/GeoLiteCityv6.dat")


###############################################################################
### DJANGO GEOIP                                                            ###
###############################################################################
GEOIP_PATH = os.path.join(PROJECT_PATH, "geoip/")


###############################################################################
### DJANGO GRAPPELLI                                                        ###
###############################################################################
GRAPPELLI_ADMIN_TITLE = "SaneSide Admin"
GRAPPELLI_AUTOCOMPLETE_LIMIT = 25
# GRAPPELLI_AUTOCOMPLETE_SEARCH_FIELDS
GRAPPELLI_SWITCH_USER = True
# GRAPPELLI_SWITCH_USER_ORIGINAL
# GRAPPELLI_SWITCH_USER_TARGET
# GRAPPELLI_CLEAN_INPUT_TYPES = False


###############################################################################
### DJANGO HAYSTACK                                                         ###
###############################################################################
INSTALLED_APPS += (
    "haystack",
)

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE":       "haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine",
        "URL":          "http://127.0.0.1:9200/",
        "INDEX_NAME":   "haystack",
    },
}
HAYSTACK_DEFAULT_OPERATOR = "AND"
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 50


###############################################################################
### DJANGO IMAGEKIT                                                         ###
###############################################################################
INSTALLED_APPS += (
    "imagekit",
)

IMAGEKIT_CACHEFILE_DIR = "CACHE/images"
IMAGEKIT_DEFAULT_CACHEFILE_BACKEND = "imagekit.cachefiles.backends.Simple"
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.JustInTime"
IMAGEKIT_CACHEFILE_NAMER = "imagekit.cachefiles.namers.hash"
IMAGEKIT_SPEC_CACHEFILE_NAMER = "imagekit.cachefiles.namers.source_name_as_path"


###############################################################################
### DJANGO MPTT                                                             ###
###############################################################################
INSTALLED_APPS += (
    "mptt",
)

MPTT_ADMIN_LEVEL_INDENT = 20


###############################################################################
### DJANGO MPTT ADMIN                                                       ###
###############################################################################
INSTALLED_APPS += (
    "django_mptt_admin",
)


###############################################################################
### DJANGO PAGINATOR                                                        ###
###############################################################################
MAX_MEMBERS_PER_PAGE = 50
MAX_MEMBERS_PER_QUERY = 500

MAX_POSTS_PER_PAGE = 20
MAX_POSTS_PER_QUERY = 100

MAX_CHALLENGES_PER_PAGE = 25
MAX_CHALLENGES_PER_QUERY = 250

MAX_ORGANIZATIONS_PER_PAGE = 25
MAX_ORGANIZATIONS_PER_QUERY = 250


###############################################################################
### DJANGO PASSWORDS                                                        ###
###############################################################################
PASSWORD_MIN_LENGTH = 6         # Defaults to 6
PASSWORD_MAX_LENGTH = 30        # Defaults to None
PASSWORD_DICTIONARY = None
PASSWORD_MATCH_THRESHOLD = 0.9  # Defaults to 0.9, should be 0.0 - 1.0, where 1.0 means exactly the same.
PASSWORD_COMMON_SEQUENCES = []  # Should be a List of Strings. See `passwords/validators.py` for default
PASSWORD_COMPLEXITY = {         # You can omit any or all of these for no Limit for that particular Set
    "UPPER":    1,              # Uppercase
    "LOWER":    1,              # Lowercase
    "LETTERS":  1,              # Either uppercase or lowercase Letters
    "DIGITS":   1,              # Digits
    "SPECIAL":  1,              # Not alphanumeric, Space or punctuation Character
    "WORDS":    0               # Words (alphanumeric Sequences, separated by a Whitespace or punctuation character)
}


###############################################################################
### DJANGO PHONE NUMBER FIELD                                               ###
###############################################################################
INSTALLED_APPS += (
    "phonenumber_field",
)

PHONENUMBER_DB_FORMAT = "INTERNATIONAL"


###############################################################################
### DJANGO REST FRAMEWORK                                                   ###
###############################################################################
INSTALLED_APPS += (
    "rest_framework",
    "rest_framework.authtoken",
)
REST_FRAMEWORK = {
    "DEFAULT_MODEL_SERIALIZER_CLASS":   "rest_framework.serializers.HyperlinkedModelSerializer",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework_jsonp.renderers.JSONPRenderer",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),

    "TEST_REQUEST_DEFAULT_FORMAT":  "json",
    "TEST_REQUEST_RENDERER_CLASSES": (
        "rest_framework.renderers.MultiPartRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.TemplateHTMLRenderer"
    ),
}


###############################################################################
### DJANGO REST FRAMEWORK SWAGGER                                           ###
###############################################################################
INSTALLED_APPS += (
    "rest_framework_swagger",
)
SWAGGER_SETTINGS = {
    "exclude_namespaces":           [],
    "api_version":                  "1.0",
    "api_path":                     "/",
    "enabled_methods": [
        "get",
        "post",
        "put",
        "patch",
        "delete",
    ],
    "api_key":                      "",
    "is_authenticated":             True,
    "is_superuser":                 False,
    "unauthenticated_user":         "django.contrib.auth.models.AnonymousUser",
    "permission_denied_handler":    "app.views.permission_denied_handler",
    "resource_access_handler":      "app.views.resource_access_handler",
    #"base_path":                    "helloreverb.com/docs",
    "info": {
        "contact":                  "artem.suvorov@gmail.com",
        "description":              "This is a sample Server Petstore Server. You can find out more about Swagger at <a href=\"http://swagger.wordnik.com\">http://swagger.wordnik.com</a> or on irc.freenode.net, #swagger. For this Sample, you can use the API Key \"special-key\" to test the authorization Filters",
        "license":                  "Apache 2.0",
        "licenseUrl":
            "http://www.apache.org/licenses/LICENSE-2.0.html",
        "termsOfServiceUrl":        "http://helloreverb.com/terms/",
        "title":                    "SaneSide - Swagger API Docs",
    },
    "doc_expansion":                "list",
}


###############################################################################
### DJANGO ROSETTA                                                          ###
###############################################################################
INSTALLED_APPS += (
    "rosetta",
)

ROSETTA_MESSAGES_PER_PAGE = 20
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True

YANDEX_TRANSLATE_KEY = "trnsl.1.1.20160321T202549Z.dc1425f58a3b7ddc.425ec99eb6632647ee447824f70d71f9dbaddb45"

AZURE_CLIENT_ID = None
AZURE_CLIENT_SECRET = None

ROSETTA_MESSAGES_SOURCE_LANGUAGE_CODE = "en"
ROSETTA_MESSAGES_SOURCE_LANGUAGE_NAME = "English"

ROSETTA_WSGI_AUTO_RELOAD = False
ROSETTA_UWSGI_AUTO_RELOAD = False

ROSETTA_EXCLUDED_APPLICATIONS = ()
ROSETTA_EXCLUDED_PATHS = ()

ROSETTA_REQUIRES_AUTH = True

ROSETTA_POFILE_WRAP_WIDTH = 0
ROSETTA_POFILENAMES = ("django.po", "djangojs.po")

ROSETTA_STORAGE_CLASS = "rosetta.storage.CacheRosettaStorage"
ROSETTA_ACCESS_CONTROL_FUNCTION = None

ROSETTA_LANGUAGE_GROUPS = False

ROSETTA_AUTO_COMPILE = True


###############################################################################
### DJANGO SEO                                                              ###
###############################################################################
INSTALLED_APPS += (
    "djangoseo",
)


###############################################################################
### DJANGO SIMPLE CAPTCHA                                                   ###
###############################################################################
INSTALLED_APPS += (
    "captcha",
)

CAPTCHA_FONT_SIZE = 22
CAPTCHA_BACKGROUND_COLOR = "#ffffff"
CAPTCHA_FOREGROUND_COLOR = "#001100"
CAPTCHA_PUNCTUATION = '''_"',.;:-'''
CAPTCHA_TIMEOUT = 5  # Minutes
CAPTCHA_LENGTH = 4  # Chars
CAPTCHA_IMAGE_BEFORE_FIELD = True
CAPTCHA_DICTIONARY_MIN_LENGTH = 0
CAPTCHA_DICTIONARY_MAX_LENGTH = 99
CAPTCHA_TEST_MODE = False


###############################################################################
### PYTHON/DJANGO SOCIAL AUTH                                               ###
###############################################################################
INSTALLED_APPS += (
    "social_django",
)

AUTHENTICATION_BACKENDS += (
    "social_core.backends.facebook.FacebookAppOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.linkedin.LinkedinOAuth",
    "social_core.backends.linkedin.LinkedinOAuth2",
    "social_core.backends.google.GoogleOAuth",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.google.GoogleOpenId",
    "social_core.backends.google.GooglePlusAuth",
    "social_core.backends.google_openidconnect.GoogleOpenIdConnect",
)

SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # One Month

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/my-profile/"
#LOGIN_ERROR_URL    = "/login-error/"

#SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/logged-in/"
#SOCIAL_AUTH_LOGIN_ERROR_URL = "/login-error/"
#SOCIAL_AUTH_LOGIN_URL = "/login-url/"
#SOCIAL_AUTH_NEW_USER_REDIRECT_URL = "/new-users-redirect-url/"
#SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = "/new-association-redirect-url/"
#SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = "/account-disconnected-redirect-url/"
#SOCIAL_AUTH_INACTIVE_USER_URL = "/inactive-user/"

#SOCIAL_AUTH_USER_MODEL = "foo.bar.User"

SOCIAL_AUTH_UUID_LENGTH = 16
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_SLUGIFY_USERNAMES = False
SOCIAL_AUTH_CLEAN_USERNAMES = True

SOCIAL_AUTH_COMPLETE_URL_NAME = "socialauth_complete"
SOCIAL_AUTH_ASSOCIATE_URL_NAME = "socialauth_associate_complete"

SOCIAL_AUTH_DEFAULT_USERNAME = lambda: random.choice([
    "Darth_Vader", "Obi-Wan_Kenobi", "R2-D2", "C-3PO", "Yoda"
])
SOCIAL_AUTH_CREATE_USERS = True

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.mail.mail_validation",
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.debug.debug",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",

    "accounts.auth_pipelines.save_profile",
)


###############################################################################
### DJANGO TAGGIT                                                           ###
###############################################################################
INSTALLED_APPS += (
    "taggit",
    "taggit_templatetags2",
)

TAGGIT_CASE_INSENSITIVE = True
TAGGIT_TAGCLOUD_MIN = 1.0
TAGGIT_TAGCLOUD_MAX = 5.0
TAGGIT_LIMIT = 32
TAGGIT_TAG_LIST_ORDER_BY = "-num_times"
TAGGIT_TAG_CLOUD_ORDER_BY = "name"


###############################################################################
### DJANGO WHITE NOISE                                                      ###
###############################################################################
WHITENOISE_MAX_AGE = 31536000


###############################################################################
### MAILING                                                                 ###
###############################################################################
EMAIL_SENDER = "no-reply@saneside.com"
EMAIL_SUPPORT = "support@saneside.com"

# --- SendGrid Gateway
EMAIL_BACKEND = "sgbackend.SendGridBackend"
SENDGRID_API_KEY = ""


###############################################################################
### PROJECT PAGES TRIGGERS                                                  ###
###############################################################################


###############################################################################
### SANESIDE SOCIAL LINKS                                                   ###
###############################################################################
PB_SOCIAL_LINKS = {
    # --- On behalf of "artem.suvorov@gamil.com" / S1
    "PB_FACEBOOK":  "https://www.facebook.com/saneside",
    # --- On behalf of "support@saneside.com"    / S1
    "PB_TWITTER":   "https://twitter.com/sanesidedotcom",
    "PB_LINKEDIN":  "#",
    "PB_GOOGLE":    "#",
    "PB_PINTEREST": "#",
    # --- On behalf of "support@saneside.com"    / S1
    "PB_INSTAGRAM": "https://www.instagram.com/sanesidedotcom",
    "PB_TUMBLR":    "#",
}


###############################################################################
### UPLOADING ATTACHMENTS                                                   ###
###############################################################################
UPLOADER_SETTINGS = {
    "default": {
        "FILE_TYPES": [
            "gif", "jpg", "jpeg", "png",
            "doc", "docx", "txt", "rtf",
        ],
        "CONTENT_TYPES": [
            "image/gif",
            "image/jpeg",
            "image/pjpeg",
            "image/png",
            "application/pdf",
            "application/msword",
            "text/plain",
            "text/rtf",
        ],
        "MAX_FILE_SIZE":    10485760,
        "MAX_FILE_NUMBER":  5,
        "AUTO_UPLOAD":      True,
    },
    "documents": {
        "FILE_TYPES": [
            "doc", "docx", "txt", "rtf",
        ],
        "CONTENT_TYPES": [
            "application/pdf",
            "application/msword",
            "text/plain",
            "text/rtf",
            ],
        "MAX_FILE_SIZE":    10485760,
        "MAX_FILE_NUMBER":  5,
        "AUTO_UPLOAD":      True,
    },
    "images": {
        "FILE_TYPES": [
            "gif", "jpg", "jpeg", "png",
        ],
        "CONTENT_TYPES": [
            "image/gif",
            "image/jpeg",
            "image/pjpeg",
            "image/png",
            ],
        "MAX_FILE_SIZE":    10485760,
        "MAX_FILE_NUMBER":  5,
        "AUTO_UPLOAD":      True,
    },
    "video": {
        "FILE_TYPES": [
            "flv", "mpg", "mpeg", "mp4",
            "avi", "mkv", "ogg",
            "wmv", "mov", "webm",
        ],
        "CONTENT_TYPES": [
            "video/mpeg",
            "video/mp4",
            "video/ogg",
            "video/quicktime",
            "video/webm",
            "video/x-ms-wmv",
            "video/x-flv",
            ],
        "MAX_FILE_SIZE":    10485760,
        "MAX_FILE_NUMBER":  5,
        "AUTO_UPLOAD":      True,
    },
    "audio": {
        "FILE_TYPES": [
            "mp3", "mp4", "ogg", "wma", "wax", "wav", "webm",
        ],
        "CONTENT_TYPES": [
            "audio/basic",
            "audio/L24",
            "audio/mp4",
            "audio/mpeg",
            "audio/ogg",
            "audio/vorbis",
            "audio/x-ms-wma",
            "audio/x-ms-wax",
            "audio/vnd.rn-realaudio",
            "audio/vnd.wave",
            "audio/webm",
            ],
        "MAX_FILE_SIZE":    10485760,
        "MAX_FILE_NUMBER":  5,
        "AUTO_UPLOAD":  True,
    }
}
