from django.contrib.sitemaps import Sitemap

from organizations.models import Organization


class OrganizationSitemap(Sitemap):
    """Sitemap."""

    changefreq = "always"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Organization.objects.filter(
            is_hidden=False)

    def lastmod(self, obj):
        return obj.created
