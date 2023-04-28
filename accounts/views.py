from django.shortcuts import render
from django.views.generic import CreateView, UpdateView
from accounts.models import User
from .forms import (RegisterClientForm,
                    RegisterDoctorForm,
                    RegisterUserForm,
                    UpdateDoctorProfileForm,
                    UpdateUserProfileForm)
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, AuthenticationForm, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from moderation.models import CertificationConfirmation, CertificationPhoto
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from moderation.forms import AddCertificationConfirmationForm
from moderation.views import AddCertificationConfirmationView
from django.db.models.functions import TruncDay
from django.db.models import Prefetch
from doctors.models import Doctor

class RegisterClientView(CreateView):
    '''Регистрация клиента'''
    form_class = RegisterClientForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('doctors:index')

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)

        return HttpResponseRedirect(self.get_success_url())

class RegisterDoctorUserView(CreateView):
    '''Создание юзера для доктора. (Поскольку у доктара большая регистрация.)'''
    form_class = RegisterUserForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:certification_confirmation')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_doctor = True
        self.object.save()
        login(self.request, self.object)

        return HttpResponseRedirect(self.get_success_url())

class CertificationConfirmationView(CreateView):
    '''Создание профиля доктора и запрос на сертификацию'''
    form_class = RegisterDoctorForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:doctor_success_register_message')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_doctor:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        qualifications = form.cleaned_data['qualifications']
        self.object = form.save(commit=False) #Модель доктора
        self.object.user = self.request.user
        self.object.save()
        print(self.object.qualifications.all())
        user_cc = CertificationConfirmation.objects.create(doctor=self.object)
        user_cc.qualifications.set(qualifications)
        for image in self.request.FILES.getlist('certification_photos'):
            CertificationPhoto.objects.create(certification_confirmation=user_cc, photo=image)

        return HttpResponseRedirect(self.get_success_url())

class LoginUserView(LoginView):
    form_class = AuthenticationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('doctors:index')

    def get_success_url(self):
        return reverse_lazy('doctors:index')

def logout_user(request):
    logout(request)
    return redirect('doctors:index')

def doctor_success_register_message(request):
    '''Сообщание для того чтобы подождать подтверждение сертификации'''
    return render(request,'accounts/doctor_success_register_message.html')

def profile(request, username):
    profile = get_object_or_404(User, username=username)
    print()
    if profile.is_doctor:
        # profile = get_object_or_404(User.objects.select_related(
        #     Prefetch('doctor', Doctor.objects.prefetch_related('visiting_time'))),
        #     username=username)
        calendar = profile.doctor.visiting_time.annotate(day=TruncDay('time')).values('day','id', 'time', 'is_booked')
        calendar_dict = {}
        for day in calendar:
            if day['day'] in calendar_dict:
                calendar_dict[day['day']].append({'id':day['id'],'time':day['time'], 'is_booked':day['is_booked']})
            else:
                calendar_dict[day['day']] = [{'time':day['time'], 'is_booked':day['is_booked']}]
        print(calendar_dict)
        return render(request,'accounts/doctor_profile.html', {'profile':profile, 'calendar':calendar_dict})
    else:
        profile = get_object_or_404(User.objects.select_related('client'), username=username)
        return render(request,'accounts/client_profile.html', {'profile':profile})

class UpdateDoctorProfileView(LoginRequiredMixin, UpdateView):
    form_class = UpdateDoctorProfileForm
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_doctor:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username':self.request.user.username})

class UpdateClientProfileView(LoginRequiredMixin, UpdateView):
    form_class = UpdateUserProfileForm
    template_name = 'accounts/login.html'

    def get_object(self, queryset=None):
        if not self.request.user.is_doctor:
            return self.request.user
        else:
            raise Http404

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username':self.request.user.username})