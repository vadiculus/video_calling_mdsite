from django import forms

class BalanceReplenishmentForm(forms.Form):
    amount = forms.IntegerField(label='Сумма')
    class Meta:
        fields = ['amount']
