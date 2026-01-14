from django import forms
from .models import Photo, Tag

class PhotoTagsForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Photo
        fields = ["tags"]


class CreateTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]

    def clean_name(self):
        name = (self.cleaned_data["name"] or "").strip()

        if not name:
            raise forms.ValidationError("Please enter a tag name.")

        # Case-insensitive duplicate check
        existing = Tag.objects.filter(name__iexact=name).first()
        if existing:
            raise forms.ValidationError(f'"{existing.name}" already exists.')

        return name

