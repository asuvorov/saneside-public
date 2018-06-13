import datetime

from django.contrib.sitemaps import Sitemap
from django.db.models import Q

from challenges.choices import (
    CHALLENGE_STATUS,
    RECURRENCE,
    )
from challenges.models import Challenge


class ChallengeSitemap(Sitemap):
    """Sitemap."""

    changefreq = "always"
    priority = 0.5
    protocol = "https"

    def items(self):
        return Challenge.objects.filter(
            Q(start_date__gte=datetime.date.today()) |
            Q(recurrence=RECURRENCE.DATELESS),
            status=CHALLENGE_STATUS.UPCOMING)

    def lastmod(self, obj):
        return obj.created
