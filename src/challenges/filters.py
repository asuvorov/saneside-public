import django_filters

from challenges.models import Challenge


class ChallengeFilter(django_filters.FilterSet):
    """Challenge Filter."""
    name = django_filters.CharFilter(
        lookup_expr="icontains")
    year = django_filters.NumberFilter(
        name="start_date",
        lookup_expr="year")
    month = django_filters.NumberFilter(
        name="start_date",
        lookup_expr="month")
    day = django_filters.NumberFilter(
        name="start_date",
        lookup_expr="day")

    class Meta:
        model = Challenge
        fields = [
            "name",
        ]
