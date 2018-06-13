from django import forms
from django.contrib.auth.models import User
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _

from annoying.functions import get_object_or_None
from captcha.fields import CaptchaField
from passwords.fields import PasswordField

from accounts.models import (
    UserPrivacyAdmins,
    UserPrivacyGeneral,
    UserPrivacyMembers,
    UserProfile,
    )


# -----------------------------------------------------------------------------
# --- LOG IN FORM
# -----------------------------------------------------------------------------
class LoginForm(forms.Form):
    """Login Form."""

    username = forms.CharField(
        label=_("Email"),
        widget=forms.TextInput(
            attrs={
                "class":        "form-control",
                "placeholder":  _("Email"),
                "value":        "",
            }))
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Password"),
                "value":        "",
            }))
    remember_me = forms.BooleanField(
        label=_("Keep me logged-in on this Computer"),
        required=False,
        initial=True)

    def add_non_field_error(self, message):
        """Docstring."""
        error_list = self.errors.setdefault(NON_FIELD_ERRORS, ErrorList())
        error_list.append(message)


# -----------------------------------------------------------------------------
# --- USER FORM
# -----------------------------------------------------------------------------
class UserForm(forms.ModelForm):
    """User Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        super(UserForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

        # self.fields["username"].required = False
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

    password = PasswordField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Password"),
                "value":        "",
            }))
    retry = forms.CharField(
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Retry"),
                "value":        "",
            }))

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "password",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("First Name"),
                    "maxlength":    30,
                }),
            "last_name": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Last Name"),
                    "maxlength":    30,
                }),
            "email": forms.EmailInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Email"),
                }),
            }

    def clean_email(self):
        """Docstring."""
        user = get_object_or_None(
            User,
            email=self.cleaned_data.get("email", "")
            )

        if user:
            raise forms.ValidationError(
                _("User already exists."))

        return self.cleaned_data["email"]

    def clean_retry(self):
        """Docstring."""
        if self.cleaned_data["retry"] != self.cleaned_data.get("password", ""):
            raise forms.ValidationError(
                _("Passwords don't match."))

        return self.cleaned_data["retry"]

    def save(self, commit=True):
        """Docstring."""
        instance = super(UserForm, self).save(commit=False)
        instance.username = self.cleaned_data["email"]

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- USER PROFILE FORM
# -----------------------------------------------------------------------------
class UserProfileForm(forms.ModelForm):
    """User Profile Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    captcha = CaptchaField()
    birth_day = forms.DateField(
        input_formats=("%m/%d/%Y",),
        widget=forms.DateInput(
            format="%m/%d/%Y",
            attrs={
                "class":    "form-control",
            }))

    class Meta:
        model = UserProfile
        fields = [
            "avatar", "nickname", "bio", "gender", "birth_day",
            "receive_newsletters",
        ]
        widgets = {
            "nickname": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Nickname"),
                    "maxlength":    30,
                }),
            "bio": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Tell us a bit about yourself."),
                    "maxlength":    1000,
                }),
            "gender": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "birth_day": forms.DateInput(
                attrs={
                    "class":        "form-control",
                }),
            }

    def clean(self):
        """Docstring."""
        cleaned_data = super(UserProfileForm, self).clean()

        return cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(UserProfileForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- USER PROFILE EDIT FORM
# -----------------------------------------------------------------------------
class UserProfileEditForm(forms.ModelForm):
    """User Profile edit Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)

        super(UserProfileEditForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

        self.fields["first_name"].initial = self.user.first_name
        self.fields["last_name"].initial = self.user.last_name
        self.fields["email"].initial = self.user.email
        self.fields["email"].required = False
        self.fields["email"].widget.attrs["class"] = "disabled"
        self.fields["email"].widget.attrs["readonly"] = True

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class":        "form-control",
                "placeholder":  _("First Name"),
                "value":        "",
                "maxlength":    30,
            }))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class":        "form-control",
                "placeholder":  _("Last Name"),
                "value":        "",
                "maxlength":    30,
            }))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class":        "form-control",
                "placeholder":  _("Email"),
                "value":        ""
            }))
    birth_day = forms.DateField(
        input_formats=("%m/%d/%Y",),
        widget=forms.DateInput(
            format="%m/%d/%Y",
            attrs={
                "class":    "form-control",
                # "type":     "date",
            }))

    class Meta:
        model = UserProfile
        fields = [
            "avatar", "nickname", "bio", "gender", "birth_day",
            "receive_newsletters",
        ]
        widgets = {
            "nickname": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Nickname"),
                    "maxlength":    30,
                }),
            "bio": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Tell us a bit about yourself."),
                    "maxlength":    1000,
                }),
            "gender": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "birth_day": forms.DateInput(
                attrs={
                    "class":        "form-control",
                    # "type":         "date",
                }),
            }

    def clean(self):
        """Docstring."""
        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(UserProfileEditForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- RESET PASSWORD FORM
# -----------------------------------------------------------------------------
class ResetPasswordForm(forms.Form):
    """Reset Password Form."""

    password = PasswordField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Password"),
                "value":        "",
            }))
    retry = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "min_length":   6,
                "max_length":   30,
                "class":        "form-control",
                "placeholder":  _("Retry"),
                "value":        "",
            }))

    def clean_retry(self):
        """Docstring."""
        if self.cleaned_data["retry"] != self.cleaned_data.get("password", ""):
            raise forms.ValidationError(
                _("Passwords don't match."))

        return self.cleaned_data["retry"]


# -----------------------------------------------------------------------------
# --- USER PRIVACY GENERAL FORM
# -----------------------------------------------------------------------------
class UserPrivacyGeneralForm(forms.ModelForm):
    """User Privacy (general) Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        super(UserPrivacyGeneralForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    class Meta:
        model = UserPrivacyGeneral
        fields = [
            "hide_profile_from_search",
            "hide_profile_from_list",
        ]
        widgets = {
            "hide_profile_from_search": forms.CheckboxInput(
                attrs={
                    "class":        "form-control",
                }),
            "hide_profile_from_list": forms.CheckboxInput(
                attrs={
                    "class":        "form-control",
                }),
            }

    def clean(self):
        """Docstring."""
        cleaned_data = super(UserPrivacyGeneralForm, self).clean()

        return cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(UserPrivacyGeneralForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- USER PRIVACY MEMBERS FORM
# -----------------------------------------------------------------------------
class UserPrivacyMembersForm(forms.ModelForm):
    """User Privacy (Members) Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        super(UserPrivacyMembersForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    class Meta:
        model = UserPrivacyMembers
        fields = [
            "profile_details", "contact_details",
            "challenges_upcoming", "challenges_completed",
            "challenges_affiliated",
            "participations_canceled", "participations_rejected",
        ]
        widgets = {
            "profile_details": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "contact_details": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "challenges_upcoming": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "challenges_completed": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "challenges_affiliated": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "participations_canceled": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "participations_rejected": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            }

    def clean(self):
        """Docstring."""
        cleaned_data = super(UserPrivacyMembersForm, self).clean()

        return cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(UserPrivacyMembersForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- USER PRIVACY ADMINS FORM
# -----------------------------------------------------------------------------
class UserPrivacyAdminsForm(forms.ModelForm):
    """User Privacy (Admins) Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        super(UserPrivacyAdminsForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    class Meta:
        model = UserPrivacyAdmins
        fields = [
            "profile_details", "contact_details",
            "challenges_upcoming", "challenges_completed",
            "challenges_affiliated",
            "participations_canceled", "participations_rejected",
        ]
        widgets = {
            "profile_details": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "contact_details": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "challenges_upcoming": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "challenges_completed": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "challenges_affiliated": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "participations_canceled": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            "participations_rejected": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            }

    def clean(self):
        """Docstring."""
        cleaned_data = super(UserPrivacyAdminsForm, self).clean()

        return cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(UserPrivacyAdminsForm, self).save(commit=False)

        if commit:
            instance.save()

        return instance
