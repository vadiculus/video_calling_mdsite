from django import forms
from .models import Qualification, Doctor, Review

class DoctorSearchForm(forms.ModelForm):

    class Meta:
        model = Doctor
        fields = ['qualifications', 'rating']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating']