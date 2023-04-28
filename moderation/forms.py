from django import forms
from .models import CertificationConfirmation

class AddCertificationConfirmationForm(forms.ModelForm):
    certification_photos = forms.ImageField(label='Фото сертификаций', widget=forms.FileInput(attrs={'multiple': True}))

    class Meta:
        model = CertificationConfirmation
        fields = ['qualifications',]
