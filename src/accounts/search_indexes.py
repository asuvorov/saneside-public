import datetime

from haystack import indexes

from accounts.models import UserProfile


# -----------------------------------------------------------------------------
# --- USER PROFILE SEARCH INDEX
# -----------------------------------------------------------------------------
class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):
    """UserProfile Index."""

    # -------------------------------------------------------------------------
    text = indexes.CharField(
        document=True,
        use_template=True)
    rendered = indexes.CharField(
        use_template=True,
        indexed=False)

    # -------------------------------------------------------------------------
    user = indexes.CharField(
        model_attr="user")
    nickname = indexes.CharField(
        model_attr="nickname",
        default="")
    bio = indexes.CharField(
        model_attr="bio",
        default="")

    created = indexes.DateTimeField(
        model_attr="created")

    def get_model(self):
        """Docstring."""
        return UserProfile

    def index_queryset(self, using=None):
        """Used when the entire Index for Model is updated."""
        return self.get_model().objects.filter(
            user__privacy_general__hide_profile_from_search=False,
            user__is_active=True,
            created__lte=datetime.date.today(),
            )
