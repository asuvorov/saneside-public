from django.contrib.sitemaps import Sitemap

from blog.choices import POST_STATUS
from blog.models import Post


class BlogPostSitemap(Sitemap):
    """Sitemap."""

    changefreq = "always"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Post.objects.filter(
            status=POST_STATUS.VISIBLE)

    def lastmod(self, obj):
        return obj.created
