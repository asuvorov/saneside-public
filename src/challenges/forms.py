import inspect

from django import forms
from django.conf import settings
from django.forms import BaseModelFormSet
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _

import pendulum

from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from djangoformsetjs.utils import formset_media_js
from taggit.forms import TagWidget
from termcolor import colored

from challenges.choices import (
    RECURRENCE,
    month_choices,
    day_of_month_choices,
    )
from challenges.models import (
    Challenge,
    Role,
    )
from core.models import TemporaryFile


# -----------------------------------------------------------------------------
# --- CHALLENGE POST/EDIT FORM
# -----------------------------------------------------------------------------
class CreateEditChallengeForm(forms.ModelForm):
    """Create/edit Challenge Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)
        self.organization_ids = kwargs.pop("organization_ids", None)
        self.tz_name = kwargs.pop("tz_name", None)

        super(CreateEditChallengeForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

        # ---------------------------------------------------------------------
        # --- Get QuerySet of the Organizations, where User is a Staff Member.
        organizations = self.user.profile.staff_member_organizations.order_by("name")
        self.fields["organization"].required = False

        if organizations:
            self.fields["organization"].queryset = organizations
            # self.fields["organization"].initial = organizations[0]

            if self.organization_ids:
                try:
                    self.fields["organization"].initial = organizations.filter(
                        id__in=self.organization_ids,
                        )[0]
                except Exception as e:
                    print colored("###" * 27, "white", "on_red")
                    print colored("### EXCEPTION @ `{module}`: {msg}".format(
                        module=inspect.stack()[0][3],
                        msg=str(e),
                        ), "white", "on_red")
        else:
            self.fields["organization"].widget = \
                self.fields["organization"].hidden_widget()

        # ---------------------------------------------------------------------
        # --- Contact Person
        self.contact_choices = [
            ("me", _("Me (%s)") % self.user.email),
            ("he", _("Affiliate different Person")),
        ]
        self.fields["contact"].choices = self.contact_choices
        self.fields["contact"].initial = "me"

        if self.instance and self.instance.is_alt_person:
            self.fields["contact"].initial = "he"

        # ---------------------------------------------------------------------
        # --- Recurrence

        # ---------------------------------------------------------------------
        # --- Date/Time
        self.fields["start_date"].required = False
        self.fields["start_time"].required = False

        # ---------------------------------------------------------------------
        # --- Time Zone
        self.fields["start_tz"].required = False

        if self.tz_name:
            self.fields["start_tz"].initial = self.tz_name
        else:
            self.fields["start_tz"].initial = settings.TIME_ZONE

    contact = forms.ChoiceField(
        widget=forms.RadioSelect())
    start_date = forms.DateField(
        input_formats=[
            "%Y-%m-%d",     # "2006-10-25"
            "%m/%d/%Y",     # "10/25/2006"
            "%m/%d/%y",     # "10/25/06"
        ],
        widget=forms.DateInput(
            format="%m/%d/%Y",
            attrs={
                "class":        "form-control",
            }))
    start_time = forms.TimeField(
        input_formats=[
            "%H:%M",
            "%I:%M%p",
            "%I:%M %p"
        ],
        widget=forms.TimeInput(
            format="%H:%M",
            attrs={
                "class":        "form-control",
            }))

    tmp_files = forms.ModelMultipleChoiceField(
        widget=forms.widgets.MultipleHiddenInput,
        queryset=TemporaryFile.objects.all(),
        required=False,
    )
    tmp_links = forms.CharField(
        label=_("Related Links"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Separate your Links with a Space"),
            }),
        required=False,
    )

    class Meta:
        model = Challenge
        fields = [
            "avatar", "name", "description", "category", "tags", "hashtag",
            "duration", "addressless", "is_alt_person",
            "alt_person_fullname", "alt_person_email", "alt_person_phone",
            "recurrence",
            "start_date", "start_time", "start_tz",
            "organization", "application", "allow_reenter",
            "accept_automatically", "acceptance_text",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Challenge Name"),
                    "maxlength":    80,
                }),
            "description": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Challenge Description"),
                    "maxlength":    1000,
                }),
            "category": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "tags": TagWidget(),
            "hashtag": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Hashtag"),
                    "maxlength":    80,
                }),
            "duration": forms.TextInput(
                attrs={
                    "class":        "form-control slider",
                }),
            "recurrence": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "alt_person_fullname": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Full Name"),
                    "maxlength":    80,
                }),
            "alt_person_email": forms.EmailInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Email"),
                    "maxlength":    80,
                }),
            "alt_person_phone": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Phone Number"),
                }),
            "start_tz": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "organization": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "application": forms.RadioSelect(),
            "acceptance_text": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Write the Feedback here..."),
                    "maxlength":    1000,
                }),
            }

    def clean_duration(self):
        """Clean `duration` Field."""
        duration = self.cleaned_data["duration"]

        if duration <= 0:
            raise forms.ValidationError(
                _("Duration should be greater, than 0"))

        return duration

    def clean(self):
        """Clean."""
        print colored("[---  DUMP   ---] CLEANED DATA : %s" % self.cleaned_data, "yellow")

        # ---------------------------------------------------------------------
        # --- Validate `name` Field
        if self.cleaned_data["name"].lower() in settings.CHALLENGE_NAME_RESERVED_WORDS:
                self._errors["name"] = self.error_class(
                    [_("Reserved Word cannot be used as a Challenge Name.")])

        # ---------------------------------------------------------------------
        # --- Validate `alt_person` Fields
        if self.cleaned_data["contact"] == "me":
            self.cleaned_data["is_alt_person"] = False
        else:
            self.cleaned_data["is_alt_person"] = True

            if not self.cleaned_data["alt_person_fullname"]:
                self._errors["alt_person_fullname"] = self.error_class(
                    [_("This Field is required.")])

                del self.cleaned_data["alt_person_fullname"]

            if not self.cleaned_data["alt_person_email"]:
                self._errors["alt_person_email"] = self.error_class(
                    [_("This Field is required.")])

                del self.cleaned_data["alt_person_email"]

            if (
                    "alt_person_phone" in self.cleaned_data and
                    not self.cleaned_data["alt_person_phone"]):
                self._errors["alt_person_phone"] = self.error_class(
                    [_("This Field is required.")])

                del self.cleaned_data["alt_person_phone"]

        # ---------------------------------------------------------------------
        # --- Validate `recurrence` Field
        if self.cleaned_data["recurrence"] == RECURRENCE.DATELESS:
            pass
        elif self.cleaned_data["recurrence"] == RECURRENCE.ONCE:
            if not self.cleaned_data["start_date"]:
                self._errors["start_date"] = self.error_class(
                    [_("This Field is required.")])

                del self.cleaned_data["start_date"]

            if self.cleaned_data["start_time"] is None:
                # Refer to `https://bugs.python.org/issue13936`
                self._errors["start_time"] = self.error_class(
                    [_("This Field is required.")])

                del self.cleaned_data["start_time"]

        # ---------------------------------------------------------------------
        # --- Validate `accept_automatically` Field
        if (
                self.cleaned_data["accept_automatically"] and
                not self.cleaned_data["acceptance_text"]):

            self._errors["acceptance_text"] = self.error_class(
                [_("This Field is required.")])

            del self.cleaned_data["acceptance_text"]

        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(CreateEditChallengeForm, self).save(commit=False)
        instance.author = self.user

        if commit:
            instance.save()

        return instance


class AddChallengeMaterialsForm(forms.ModelForm):
    """Add the Challenge reporting Materials Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        super(AddChallengeMaterialsForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    tmp_files = forms.ModelMultipleChoiceField(
        widget=forms.widgets.MultipleHiddenInput,
        queryset=TemporaryFile.objects.all(),
        required=False,
    )
    tmp_links = forms.CharField(
        label=_("Related Links"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Separate your Links with a Space"),
            }),
        required=False,
    )

    class Meta:
        model = Challenge
        fields = [
            "achievements",
        ]
        widgets = {
            "achievements": CKEditorUploadingWidget(),
        }

    def clean(self):
        """Clean."""
        print colored("[---  DUMP   ---] CLEANED DATA : %s" % self.cleaned_data, "yellow")

        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(AddChallengeMaterialsForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- ROLE FORM & FORMSET
# -----------------------------------------------------------------------------
class RoleForm(forms.ModelForm):
    """Role Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)

        super(RoleForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    class Media(object):
        js = formset_media_js + (
            # Other form media here
        )

    class Meta:
        model = Role
        fields = [
            "name", "quantity",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Name")
                }),
            "quantity": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Qty")
                }),
            }

    def clean(self):
        """Docstring."""
        print colored("[---  DUMP   ---] CLEANED DATA : %s" % self.cleaned_data, "yellow")

        try:
            if not self.cleaned_data["DELETE"]:
                # -------------------------------------------------------------
                # --- Validate `name` Field
                if not self.cleaned_data["name"]:
                    self._errors["name"] = self.error_class(
                        [_("This Field is required.")])

                    del self.cleaned_data["name"]

                # -------------------------------------------------------------
                # --- Validate `quantity` Field
                if not self.cleaned_data["quantity"]:
                    self._errors["quantity"] = self.error_class(
                        [_("This Field is required.")])

                    del self.cleaned_data["quantity"]

        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(RoleForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


class RoleModelFormSet(BaseModelFormSet):
    """Docstring."""

    def clean(self):
        """Docstring."""
        super(RoleModelFormSet, self).clean()


RoleFormSet = modelformset_factory(
    Role, form=RoleForm, formset=RoleModelFormSet,
    max_num=10, extra=0, can_delete=True)


# -----------------------------------------------------------------------------
# --- CHALLENGE FILTER FORM
# -----------------------------------------------------------------------------
class FilterChallengeForm(forms.Form):
    """Filter Challenge Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.qs = kwargs.pop("qs", None)

        super(FilterChallengeForm, self).__init__(*args, **kwargs)

        # ---------------------------------------------------------------------
        # --- Pre-populate Form Fields.
        try:
            if self.qs.exists():
                start_year = self.qs.first().start_date.year
                end_year = self.qs.last().start_date.year

                self.fields["year"].choices = [
                    (str(year), str(year)) for year in range(start_year, end_year+1)
                ]
            else:
                this_year = pendulum.today().year

                self.fields["year"].choices = [
                    (str(year), str(year)) for year in range(this_year, this_year+3)
                ]

            self.fields["month"].choices = month_choices
            self.fields["day"].choices = day_of_month_choices[:-1]
        except:
            del self.fields["year"]
            del self.fields["month"]
            del self.fields["day"]

    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Challenge Name"),
            }),
        required=False,
    )
    year = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class":        "form-control selectpicker",
                "placeholder":  _("Year"),
            }),
        required=False,
        )
    month = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class":        "form-control selectpicker",
                "placeholder":  _("Month"),
            }),
        required=False,
        )
    day = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class":        "form-control selectpicker",
                "placeholder":  _("Day"),
            }),
        required=False,
        )
