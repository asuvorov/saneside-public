from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from taggit.forms import TagWidget
from termcolor import colored

from core.models import TemporaryFile
from organizations.models import Organization


# -----------------------------------------------------------------------------
# --- CREATE/EDIT ORGANIZATION FORM
# -----------------------------------------------------------------------------
class CreateEditOrganizationForm(forms.ModelForm):
    """Create/edit Organization Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)
        super(CreateEditOrganizationForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

        self.contact_choices = [
            ("me", _("Me (%s)") % (self.user.email)),
            ("he", _("Affiliate different Person")),
        ]
        self.fields["contact"].choices = self.contact_choices
        self.fields["contact"].initial = "me"

        if self.instance and self.instance.is_alt_person:
            self.fields["contact"].initial = "he"

        # ---------------------------------------------------------------------
        # --- Modify Fields
        self.fields["is_hidden"].help_text = _(
            "You can make your Organization hidden from the Public, so only Subscribers and Members, invited by you, will be able to see the Organization's Activity and sign up for its Challenges (Events).")

    contact = forms.ChoiceField(
        widget=forms.RadioSelect())

    tmp_files = forms.ModelMultipleChoiceField(
        widget=forms.widgets.MultipleHiddenInput,
        queryset=TemporaryFile.objects.all(),
        required=False,
    )
    tmp_links = forms.CharField(
        label="Related Links",
        widget=forms.TextInput(
            attrs={
                "placeholder":  _("Separate your Links with a Space"),
            }),
        required=False,
    )

    class Meta:
        model = Organization
        fields = [
            "avatar", "name", "description", "tags", "hashtag",
            "addressless", "is_hidden", "website", "video", "email",
            "is_alt_person", "alt_person_fullname",
            "alt_person_email", "alt_person_phone",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Organization Name"),
                    "maxlength":    80,
                }),
            "description": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Organization Description"),
                    "maxlength":    1000,
                }),
            "tags": TagWidget(),
            "hashtag": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Hashtag"),
                    "maxlength":    80,
                }),
            "website": forms.URLInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Website"),
                }),
            "video": forms.URLInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Embedded Video (Link)"),
                }),
            "email": forms.EmailInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Organization Email"),
                    "maxlength":    100,
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
                    "maxlength":    100,
                }),
            "alt_person_phone": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Phone Number"),
                }),
            }

    def clean(self):
        """Clean."""
        print colored("[---  DUMP   ---] CLEANED DATA : %s" % self.cleaned_data, "yellow")

        # ---------------------------------------------------------------------
        # --- Validate `name` Field
        if self.cleaned_data["name"].lower() in settings.ORGANIZATION_NAME_RESERVED_WORDS:
                self._errors["name"] = self.error_class(
                    [_("Reserved Word cannot be used as an Organization Name.")])

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

        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(CreateEditOrganizationForm, self).save(commit=False)
        instance.author = self.user

        if commit:
            instance.save()

        return instance
