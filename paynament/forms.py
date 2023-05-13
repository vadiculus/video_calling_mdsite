from django import forms
from .models import SiteBalance

class BalanceReplenishmentForm(forms.Form):
    amount = forms.IntegerField(label='Сумма')
    class Meta:
        fields = ['amount']

class SiteBalanceUpdateForm(forms.ModelForm):
    class Meta:
        model = SiteBalance
        fields = ['percent']

