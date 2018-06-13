from haystack import indexes

from foro.models import (
    Forum,
    Topic,
    Post,
    )


# -----------------------------------------------------------------------------
# --- FORUM SEARCH INDEX
# -----------------------------------------------------------------------------
class ForumIndex(indexes.SearchIndex, indexes.Indexable):
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
    title = indexes.CharField(
        model_attr="title")
    description = indexes.CharField(
        model_attr="description",
        default="")

    created = indexes.DateTimeField(
        model_attr="created")

    def get_model(self):
        """Docstring."""
        return Forum

    def index_queryset(self, using=None):
        """Used when the entire Index for Model is updated."""
        return self.get_model().objects.all()


# -----------------------------------------------------------------------------
# --- FORUM TOPIC SEARCH INDEX
# -----------------------------------------------------------------------------
class ForumTopicIndex(indexes.SearchIndex, indexes.Indexable):
    """Forum Topic Index."""

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
    title = indexes.CharField(
        model_attr="title")
    description = indexes.CharField(
        model_attr="description",
        default="")

    created = indexes.DateTimeField(
        model_attr="created")

    def get_model(self):
        """Docstring."""
        return Topic

    def index_queryset(self, using=None):
        """Used when the entire Index for Model is updated."""
        return self.get_model().objects.all()


# -----------------------------------------------------------------------------
# --- FORUM TOPIC POST SEARCH INDEX
# -----------------------------------------------------------------------------
class ForumTopicPostIndex(indexes.SearchIndex, indexes.Indexable):
    """Forum Topic Index."""

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
    title = indexes.CharField(
        model_attr="title")
    body = indexes.CharField(
        model_attr="body",
        default="")

    created = indexes.DateTimeField(
        model_attr="created")

    def get_model(self):
        """Docstring."""
        return Post

    def index_queryset(self, using=None):
        """Used when the entire Index for Model is updated."""
        return self.get_model().objects.all()
