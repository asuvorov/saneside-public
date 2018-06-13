from haystack import indexes

from home.models import FAQ


# -----------------------------------------------------------------------------
# --- FAQ SEARCH INDEX
# -----------------------------------------------------------------------------
class FAQIndex(indexes.SearchIndex, indexes.Indexable):
    """Forum Index."""

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
    question = indexes.CharField(
        model_attr="question")
    answer = indexes.CharField(
        model_attr="answer",
        default="")

    created = indexes.DateTimeField(
        model_attr="created")

    def get_model(self):
        """Docstring."""
        return FAQ

    def index_queryset(self, using=None):
        """Used when the entire Index for Model is updated."""
        return self.get_model().objects.all()
