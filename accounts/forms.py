from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User, Client
from doctors.models import Doctor

class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','full_name', 'email', 'photo', 'password1', 'password2']

class RegisterClientForm(UserCreationForm):

    def save(self, commit=True):
        user = super().save(commit)
        client = Client.objects.create(user=user)
        return user

    class Meta:
        model = User
        fields = ['username','full_name', 'email', 'photo', 'password1', 'password2']

class RegisterDoctorForm(forms.ModelForm):
    certification_photos = forms.ImageField(help_text='От 1 до 5 фото',
        label='Photo certification',
        widget=forms.FileInput(attrs={'multiple': True}))
        
    class Meta:
        model = Doctor
        fields = ['qualifications', 'bio', 'service_cost']
        widgets = {
            'qualifications': forms.CheckboxSelectMultiple(attrs={'help_text':'От 1 до 5 фото'})
        }
class UpdateDoctorProfileForm(forms.ModelForm):
    photo = forms.ImageField(label='Photo',required=False)
    def save(self, commit=True):
        doctor = super().save(commit)
        photo = self.cleaned_data.get('photo')
        if photo: doctor.user.photo = photo; doctor.user.save()
        return doctor

    class Meta:
        model = Doctor
        fields = ['photo', 'bio', 'service_cost']

class UpdateUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'photo']