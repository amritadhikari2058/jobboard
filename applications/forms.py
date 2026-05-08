from django import forms
from .models import Application, ApplicationLink
from django.forms import inlineformset_factory


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            "resume",
            "cover_letter",
            "experience",
            "skills",
            "availability_type",
            "availability_period",
            "expected_salary",
        ]

        widgets = {
            "resume": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "cover_letter": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write your cover letter...",
                    "rows": 4,
                }
            ),
            "experience": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Describe your experience...",
                    "rows": 3,
                }
            ),
            "skills": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Django, React, PostgreSQL",
                }
            ),
            "availability_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "availability_period": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Immediate, 2 weeks",
                }
            ),
            "expected_salary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Expected salary",
                }
            ),
        }


class ApplicationLinkForm(forms.ModelForm):
    class Meta:
        model = ApplicationLink
        fields = ["link_type", "url"]

        widgets = {
            "link_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter link (GitHub, LinkedIn, etc.)",
                }
            ),
        }


ApplicationLinkFormSet = inlineformset_factory(
    parent_model=Application,
    model=ApplicationLink,
    form=ApplicationLinkForm,
    extra=1,
    can_delete=True,
)
