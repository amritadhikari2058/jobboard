from django import forms
from .models import Job
from users.models import UserProfile


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "location", "description", "categories"]
        widgets = {"categories": forms.CheckboxSelectMultiple()}


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio", "profile_pic", "skills", "phone", "location", "resume"]
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", 'rows':3}),
            "skills": forms.Textarea(attrs={"class": "form-control", 'rows':3}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
        }
