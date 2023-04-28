from django import forms
from .models import Qualification, Doctor

class DoctorSearchForm(forms.ModelForm):

    class Meta:
        model = Doctor
        fields = ['qualifications', 'rating']