from django.contrib.sitemaps import Sitemap

from foro.models import (
    Forum,
    Topic,
    )


class ForumSitemap(Sitemap):
    """Sitemap."""

    changefreq = "always"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Forum.objects.all()

    def lastmod(self, obj):
        return obj.created


class ForumTopicSitemap(Sitemap):
    """Sitemap."""

    changefreq = "always"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Topic.objects.all()

    def lastmod(self, obj):
        return obj.created
