from django import forms
from .models import VisitingTime

class VisitingTimeForm(forms.ModelForm):
    time = forms.DateTimeField(widget=forms.DateTimeInput())

    class Meta:
        model = VisitingTime
        fields = ['time', 'max_time']