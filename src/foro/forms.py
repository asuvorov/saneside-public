from django import forms
from django.utils.translation import ugettext_lazy as _

from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from foro.models import (
    Section,
    Forum,
    Topic,
    Post,
    )


# -----------------------------------------------------------------------------
# --- FORUM CREATE/EDIT FORM
# -----------------------------------------------------------------------------
class CreateEditForumForm(forms.ModelForm):
    """Create/edit Forum Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)

        super(CreateEditForumForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

        self.fields["section"].queryset = Section.objects.all()

    class Meta:
        model = Forum
        fields = [
            "title", "description", "style_css", "section", "author",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Forum Title"),
                    "maxlength":    80,
                }),
            "description": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Forum Description"),
                    "maxlength":    1000,
                }),
            "style_css": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _(
                        "Style CSS, e.g. <i class='fa fa-fw fa-4x fa-exclamation-triangle' style='color:yellow;'></i>"),
                    "maxlength":    255,
                }),
            "section": forms.Select(
                attrs={
                    "class":        "form-control selectpicker",
                }),
            }

    def clean(self):
        """Docstring."""
        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(CreateEditForumForm, self).save(commit=False)
        instance.author = self.user

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- TOPIC CREATE/EDIT FORM
# -----------------------------------------------------------------------------
class CreateEditTopicForm(forms.ModelForm):
    """Create/edit Topic Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)
        self.forum = kwargs.pop("forum", None)

        super(CreateEditTopicForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    class Meta:
        model = Topic
        fields = [
            "title", "description", "author",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Topic Title"),
                    "maxlength":    80,
                }),
            "description": forms.Textarea(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Topic Description"),
                    "maxlength":    1000,
                }),
            }

    def clean(self):
        """Docstring."""
        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(CreateEditTopicForm, self).save(commit=False)

        if self.user:
            instance.author = self.user

        if self.forum:
            instance.forum = self.forum

        if commit:
            instance.save()

        return instance


# -----------------------------------------------------------------------------
# --- TOPIC POST CREATE/EDIT FORM
# -----------------------------------------------------------------------------
class CreateEditTopicPostForm(forms.ModelForm):
    """Create/edit Topic Post Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)
        self.topic = kwargs.pop("topic", None)
        self.parent = kwargs.pop("parent", None)

        super(CreateEditTopicPostForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    class Meta:
        model = Post
        fields = [
            "title", "body", "author",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Post Title"),
                    "maxlength":    80,
                }),
            "body": CKEditorUploadingWidget(),
            }

    def clean(self):
        """Docstring."""
        return self.cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(CreateEditTopicPostForm, self).save(commit=False)

        if self.user:
            instance.author = self.user

        if self.topic:
            instance.topic = self.topic

        if self.parent:
            instance.parent = self.parent

        if commit:
            instance.save()

        return instance
