from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _

from rest_framework import serializers

from accounts.models import UserProfile
from core.models import (
    Address,
    Phone,
    )


# -----------------------------------------------------------------------------
# --- Authorization
# -----------------------------------------------------------------------------
class AuthTokenSerializer(serializers.Serializer):
    """Auth Token Serializer."""

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        """Validate."""
        username = attrs.get("username").lower()
        password = attrs.get("password")

        if username and password:
            user = authenticate(
                username=username,
                password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        _("User Account is disabled."))

                attrs["user"] = user

                return attrs
            else:
                raise serializers.ValidationError(
                    _("Unable to login with provided Credentials."))
        else:
            raise serializers.ValidationError(
                _("Must include \"username\" and \"password\""))


# -----------------------------------------------------------------------------
# --- Version
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# --- Autocomplete
# -----------------------------------------------------------------------------
class AutocompleteMemberSerializer(serializers.HyperlinkedModelSerializer):
    """Autocomplete Member Serializer."""

    uuid = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "uuid",
            "label",
            "value",
            "avatar",
            )

    def get_uuid(self, obj):
        """Get User ID."""
        return obj.user_id

    def get_label(self, obj):
        """Get Label."""
        try:
            return u"%s | %s" % (
                obj.full_name,
                obj.address.short_address
            )
        except Exception as e:
            return u"%s " % (
                obj.full_name
            )

    def get_value(self, obj):
        """Get Value."""
        try:
            return u"%s | %s" % (
                obj.full_name,
                obj.address.short_address
            )
        except Exception as e:
            return u"%s " % (
                obj.full_name
            )


# -----------------------------------------------------------------------------
# --- Core
# -----------------------------------------------------------------------------
class AddressSerializer(serializers.HyperlinkedModelSerializer):
    """Address Serializer."""

    class Meta:
        model = Address
        fields = (
            "address_1",
            "address_2",
            "city",
            "zip_code",
            "province",
            "country",
            )


class PhoneSerializer(serializers.HyperlinkedModelSerializer):
    """Phone Number Serializer."""

    class Meta:
        model = Phone
        fields = (
            "phone_number",
            "mobile_phone_number",
            )
