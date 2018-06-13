from django import forms
from django.utils.translation import ugettext_lazy as _

from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from taggit.forms import TagWidget

from blog.models import Post


# -----------------------------------------------------------------------------
# --- BLOG POST CREATE/EDIT FORM
# -----------------------------------------------------------------------------
class CreateEditPostForm(forms.ModelForm):
    """Create/edit Post Form."""

    def __init__(self, *args, **kwargs):
        """Docstring."""
        self.user = kwargs.pop("user", None)

        super(CreateEditPostForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.id:
            pass

    class Meta:
        model = Post
        fields = [
            "avatar", "title", "description", "content", "tags", "hashtag",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Post Title"),
                    "maxlength":    80,
                }),
            "description": CKEditorUploadingWidget(),
            "content": CKEditorUploadingWidget(),
            "tags": TagWidget(),
            "hashtag": forms.TextInput(
                attrs={
                    "class":        "form-control",
                    "placeholder":  _("Hashtag"),
                    "maxlength":    80,
                }),
            }

    def clean(self):
        """Docstring."""
        cleaned_data = super(CreateEditPostForm, self).clean()

        return cleaned_data

    def save(self, commit=True):
        """Docstring."""
        instance = super(CreateEditPostForm, self).save(commit=False)
        instance.author = self.user

        if commit:
            instance.save()

        return instance
