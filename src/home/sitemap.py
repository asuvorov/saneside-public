from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class HomeSitemap(Sitemap):
    """Sitemap."""

    changefreq = "always"
    priority = 0.5
    protocol = "https"

    def items(self):
        return [
            "account-list",
            "account-near-you-list",
            "account-might-know-list",
            "account-new-list",
            "account-online-list",
            "signup",
            "post-list",
            "challenge-list",
            "challenge-near-you-list",
            "challenge-new-list",
            "challenge-dateless-list",
            "challenge-featured-list",
            "forum-list",
            "index",
            "privacy-policy",
            "user-agreement",
            "our-team",
            "our-partners",
            "about-us",
            "contact-us",
            "faq",
            "organization-list",
            "organization-directory",
            "haystack_search",
        ]

    def location(self, item):
        return reverse(item)
