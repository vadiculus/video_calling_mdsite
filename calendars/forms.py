from django import forms
from .models import VisitingTime

class VisitingTimeForm(forms.ModelForm):
    time = forms.DateTimeField(widget=forms.DateTimeInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = VisitingTime
        fields = ['time', 'max_time']