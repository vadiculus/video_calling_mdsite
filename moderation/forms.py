from django import forms
from .models import CertificationConfirmation, Complaint, StandardComplaint
from django.db.models import Q
from doctors.models import Qualification

class AddCertificationConfirmationForm(forms.ModelForm):
    certification_photos = forms.ImageField(label='Фото сертификаций', widget=forms.FileInput(attrs={'multiple': True}))
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qualifications'] = forms.ModelMultipleChoiceField(
                 label='Квалификации',
                 queryset=Qualification.objects.exclude(doctors__in=[user.doctor]),
                 widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = CertificationConfirmation
        fields = ['qualifications']

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['cause']

class ConflictCauseForm(forms.Form):
    cause = forms.CharField(label='Причина не возврата денег', widget=forms.Textarea())
    class Meta:
        fields = '__all__'

class CopmlaintCauseForm(forms.ModelForm):
    cause = forms.CharField(label='Причина', widget=forms.Textarea())
    class Meta:
        model = StandardComplaint
        fields = ['cause']

class CanselConfirmationCauseForm(forms.Form):
    cause = forms.CharField(label='Причина отклонения', widget=forms.Textarea())
    class Meta:
        fields = '__all__'

class MailAdminForm(forms.Form):
    body = forms.CharField(label='Текст',widget=forms.Textarea())
    class Meta:
        fields = '__all__'
