from django import forms
from .models import CertificationConfirmation
from django.db.models import Q
from doctors.models import Qualification

class AddCertificationConfirmationForm(forms.ModelForm):
    certification_photos = forms.ImageField(label='Фото сертификаций', widget=forms.FileInput(attrs={'multiple': True}))
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qualifications'] = forms.ModelMultipleChoiceField\
            (queryset=Qualification.objects.exclude(doctors__in=[user.doctor]))

    class Meta:
        model = CertificationConfirmation
        fields = ['qualifications']
