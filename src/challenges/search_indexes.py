import datetime

from django.db.models import Q

from haystack import indexes

from challenges.choices import (
    CHALLENGE_STATUS,
    RECURRENCE,
    )
from challenges.models import Challenge


# -----------------------------------------------------------------------------
# --- CHALLENGE SEARCH INDEX
# -----------------------------------------------------------------------------
class ChallengeIndex(indexes.SearchIndex, indexes.Indexable):
    """Challenge Index."""

    # -------------------------------------------------------------------------
    text = indexes.CharField(
        document=True,
        use_template=True)
    rendered = indexes.CharField(
        use_template=True,
        indexed=False)

    # -------------------------------------------------------------------------
    author = indexes.CharField(
        model_attr="author")
    name = indexes.CharField(
        model_attr="name")
    description = indexes.CharField(
        model_attr="description",
        default="")

    created = indexes.DateTimeField(
        model_attr="created")

    def get_model(self):
        """Docstring."""
        return Challenge

    def index_queryset(self, using=None):
        """Used when the entire Index for Model is updated."""
        return self.get_model().objects.filter(
            Q(organization=None) |
            Q(organization__is_hidden=False),
            Q(recurrence=RECURRENCE.DATELESS) |
            Q(start_date__gte=datetime.date.today()),
            status=CHALLENGE_STATUS.UPCOMING,
            )
