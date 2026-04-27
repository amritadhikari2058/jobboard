from django import forms
from .models import Job, UserProfile

class JobForm(forms.ModelForm):
    class Meta:
        model=Job
        fields=['title', 'location', 'description', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple()
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_pic', 'skills', 'phone', 'location', 'resume']