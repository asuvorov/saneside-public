from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _

from rest_framework import serializers

from organizations.models import OrganizationGroup


class OrganizationGroupSerializer(serializers.HyperlinkedModelSerializer):
    """Organization Group Serializer."""

    class Meta:
        model = OrganizationGroup
        fields = (
            "id",
            "organization_id",
            "name",
            "description",
            )
