import datetime

from haystack import indexes

from organizations.models import Organization


# -----------------------------------------------------------------------------
# --- ORGANIZATION SEARCH INDEX
# -----------------------------------------------------------------------------
class OrganizationIndex(indexes.SearchIndex, indexes.Indexable):
    """Organization Index."""

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

    website = indexes.CharField(
        model_attr="website",
        default="")
    video = indexes.CharField(
        model_attr="video",
        default="")
    email = indexes.CharField(
        model_attr="email",
        default="")

    created = indexes.DateTimeField(
        model_attr="created")

    def get_model(self):
        """Docstring."""
        return Organization

    def index_queryset(self, using=None):
        """Used when the entire Index for Model is updated."""
        return self.get_model().objects.filter(
            is_deleted=False,
            is_hidden=False,
            created__lte=datetime.date.today(),
            )
