from django import forms
from django.forms import BaseModelFormSet
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _

from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from djangoformsetjs.utils import formset_media_js
from termcolor import colored

from core.models import (
    Address,
    Newsletter,
    Phone,
    SocialLink,
    )


# -----------------------------------------------------------------------------
# --- ADDRESS FORM
# -----------------------------------------------------------------------------
class AddressForm(forms.ModelForm):
    """Address Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.required = kwargs.pop("required", False)
        self.country_code = kwargs.pop("country_code", None)

        super(AddressForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            pass

        if self.required:
            self.fields["address_1"].required = True
            self.fields["city"].required = True
            self.fields["zip_code"].required = True
            self.fields["country"].required = True

        # Override countries order in choice-list
        # self.fields["country"].choices = COUNTRIES

        if self.country_code:
            self.fields["country"].initial = self.country_code
        else:
            self.fields["country"].initial = "US"

    class Meta:
        model = Address
        fields = [
            "address_1", "address_2", "city",
            "zip_code", "province", "country",
            "notes",
        ]
        widgets = {
            "address_1": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Address Line #1"),
                    "maxlength":    80,
                }),
            "address_2": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Address Line #2"),
                    "maxlength":    80,
                }),
            "city": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("City"),
                    "maxlength":    80,
                }),
            "zip_code": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Zip/Postal Code"),
                }),
            "province": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("State/Province"),
                    "maxlength":    80,
                }),
            "country": forms.Select(
                attrs={
                    "class":            "form-control selectpicker",
                    # "data-live-search": "true",
                }),
            "notes": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Enter your Notes here..."),
                }),
            }

    def clean(self):
        """Docstring."""
        cleaned_data = super(AddressForm, self).clean()

        return cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(AddressForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- PHONE FORM
# -----------------------------------------------------------------------------
class PhoneForm(forms.ModelForm):
    """Phone Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.required = kwargs.pop("required", False)
        super(PhoneForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            pass

        if self.required:
            self.fields["phone_number"].required = True

    class Meta:
        model = Phone
        fields = [
            "phone_number", "mobile_phone_number",
            "phone_number_ext", "mobile_phone_number_ext",
        ]
        widgets = {
            "phone_number": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Phone Number"),
                }),
            "phone_number_ext": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Ext."),
                    "maxlength":    8,
                }),
            "mobile_phone_number": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Mobile Phone Number"),
                }),
            "mobile_phone_number_ext": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Ext."),
                    "maxlength":    8,
                }),
            }

    def clean(self):
        """Docstring."""
        cleaned_data = super(PhoneForm, self).clean()

        return cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(PhoneForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- NEWSLETTER CREATE FORM
# -----------------------------------------------------------------------------
class CreateNewsletterForm(forms.ModelForm):
    """Create Newsletter Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)

        super(CreateNewsletterForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            pass

    class Meta:
        model = Newsletter
        fields = [
            "title", "content",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Newsletter Title"),
                    "maxlength":    80,
                }),
            "content": CKEditorUploadingWidget(),
            }

    def clean(self):
        """Docstring."""
        cleaned_data = super(CreateNewsletterForm, self).clean()

        return cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(CreateNewsletterForm, self).save(commit=False)
        instance.author = self.user

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- SOCIAL LINK FORM & FORMSET
# -----------------------------------------------------------------------------
class SocialLinkForm(forms.ModelForm):
    """Social Link Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)

        super(SocialLinkForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    class Media(object):
        js = formset_media_js + (
            # Other form media here
        )

    class Meta:
        model = SocialLink
        fields = [
            "social_app", "url",
        ]
        widgets = {
            "social_app": forms.Select(
                attrs={
                    # "class":        "form-control selectpicker",
                    "class":        "form-control",
                }),
            "url": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("URL"),
                }),
            }

    def clean(self):
        """Docstring."""
        print colored("[---  DUMP   ---] CLEANED DATA : %s" % self.cleaned_data, "yellow")

        try:
            if not self.cleaned_data["DELETE"]:
                # -----------------------------------------------------------------
                # --- Validate `url` Field
                if not self.cleaned_data["url"]:
                    self._errors["url"] = self.error_class(
                        [_("This Field is required.")])

                    del self.cleaned_data["url"]

        except Exception as e:
            print "### EXCEPTION : %s" % str(e)

        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(SocialLinkForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


class SocialLinkModelFormSet(BaseModelFormSet):
    """Docstring."""

    def clean(self):
        """Docstring."""
        super(SocialLinkModelFormSet, self).clean()

        """
        for form in self.forms:
            if not form.cleaned_data["url"]:
                form._errors["url"] = form.error_class(
                    [_("This Field is required.")])

                del form.cleaned_data["url"]
        """


SocialLinkFormSet = modelformset_factory(
    SocialLink, form=SocialLinkForm, formset=SocialLinkModelFormSet,
    max_num=10, extra=0, can_delete=True)
