from django import forms
from .models import Qualification, Doctor, Review

class DoctorSearchForm(forms.ModelForm):
    qualifications = forms.ModelMultipleChoiceField(label='Qualifications',
                                                    required=False,
                                                    queryset=Qualification.objects.all(),
                                                    widget=forms.CheckboxSelectMultiple())
    rating = forms.IntegerField(label='Rating', max_value=5)
    class Meta:
        model = Doctor
        fields = ['qualifications', 'rating']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']