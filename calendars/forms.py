from django import forms
from .models import VisitingTime
from django.core.validators import ValidationError
import datetime
import pytz

def visiting_time_validator(value):
    if value > pytz.UTC.localize(datetime.datetime.now()):
        return True
    else:
        raise ValidationError('Эта дата уже прошла. Поставьте дату на будущее время')

class VisitingTimeForm(forms.ModelForm):
    timezone = forms.CharField(max_length=200, widget=forms.HiddenInput())
    time = forms.DateTimeField(label='Дата и время', widget=forms.DateTimeInput(), validators=[visiting_time_validator])

    class Meta:
        model = VisitingTime
        fields = ['time', 'max_time']