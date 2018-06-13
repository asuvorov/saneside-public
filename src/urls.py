from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from rest_framework_swagger.views import get_swagger_view

from accounts.sitemap import AccountSitemap
from blog.sitemap import BlogPostSitemap
from challenges.sitemap import ChallengeSitemap
from home.sitemap import HomeSitemap
from foro.sitemap import (
    ForumSitemap,
    ForumTopicSitemap,
    )
from organizations.sitemap import OrganizationSitemap


admin.autodiscover()

schema_view = get_swagger_view(title="SaneSide API")


sitemaps = {
    "accounts":         AccountSitemap,
    "blog":             BlogPostSitemap,
    "challenges":       ChallengeSitemap,
    "home":             HomeSitemap,
    "forum":            ForumSitemap,
    "forum_topics":     ForumTopicSitemap,
    "organizations":    OrganizationSitemap,
}


urlpatterns = [
    url(r"", include("social_django.urls", namespace="social")),
    url(r"^", include("cyborg.urls")),

    url(r"^ckeditor/", include("ckeditor_uploader.urls")),
    url(r"^grappelli/", include("grappelli.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^captcha/", include("captcha.urls")),
    url(r"^docs/", schema_view),
    url(r"^i18n/", include("django.conf.urls.i18n")),
    url(r"^rosetta/", include("rosetta.urls")),
    url(r"^search/", include("haystack.urls")),
    url(r"^sitemap\.xml$", sitemap, {
            "sitemaps":     sitemaps,
        },
        name="django.contrib.sitemaps.views.sitemap"),

    url(r"^", include("home.urls")),
    url(r"^accounts/", include("accounts.urls")),
    url(r"^api/v1/", include("api.v1.urls")),
    url(r"^blog/", include("blog.urls")),
    url(r"^challenges/", include("challenges.urls")),
    url(r"^core/", include("core.urls")),
    url(r"^forum/", include("foro.urls")),
    url(r"^invites/", include("invites.urls")),
    url(r"^organizations/", include("organizations.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "core.views.handler400"
handler403 = "core.views.handler403"
handler404 = "core.views.handler404"
handler500 = "core.views.handler500"

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        url(r"^debug/", include(debug_toolbar.urls)),
    ]
