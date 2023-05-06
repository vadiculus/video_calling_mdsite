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
from django.db import transaction
from calendars.forms import VisitingTimeForm
from paynament.models import Balance
from doctors.utils import require_clients
import datetime

class RegisterClientView(CreateView):
    '''Регистрация клиента'''
    form_class = RegisterClientForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('doctors:index')

    def form_valid(self, form):
        self.object = form.save()
        Balance.objects.create(user=self.object)
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
        Balance.objects.create(user=self.object)
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
        if hasattr(request.user, 'doctor'):
            return HttpResponseRedirect(reverse_lazy('accounts:update_doctor_profile'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        qualifications = form.cleaned_data['qualifications']

        self.object = form.save(commit=False) #Модель доктора
        self.object.user = self.request.user
        with transaction.atomic():
            try:
                self.object.save()
            except:
                return HttpResponseRedirect(reverse_lazy('accounts:update_doctor_profile'))
            user_cc = CertificationConfirmation.objects.create(doctor=self.object)
            user_cc.qualifications.set(qualifications)
            for image in self.request.FILES.getlist('certification_photos'):
                CertificationPhoto.objects.create(certification_confirmation=user_cc, photo=image)
        return HttpResponseRedirect(self.get_success_url())

class LoginUserView(LoginView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
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
    user = get_object_or_404(User, username=username)
    if not user.is_banned:
        if user.is_doctor:
            try:
                doctor = user.doctor
            except Doctor.DoesNotExist:
                if user == request.user:
                    return render(request, 'accounts/doctor_without_profile.html', {'page_user': user})
                else:
                    raise Http404
            # profile = get_object_or_404(User.objects.select_related(
            #     Prefetch('doctor', Doctor.objects.prefetch_related('visiting_time'))),
            #     username=username)
            if user == request.user:
                calendar = user.doctor.visiting_time.annotate(day=TruncDay('time'))\
                    .values('day','id', 'time', 'is_booked')
            else:
                calendar = user.doctor.visiting_time.annotate(day=TruncDay('time'))\
                    .filter(is_booked=False)\
                    .values('day', 'id', 'time', 'is_booked')
            calendar_dict = {}
            for day in calendar:
                if day['day'] in calendar_dict:
                    calendar_dict[day['day']].append({'id':day['id'], 'time':day['time'], 'is_booked':day['is_booked']})
                else:
                    calendar_dict[day['day']] = [{'id':day['id'], 'time':day['time'], 'is_booked':day['is_booked']}]
            return render(request,'accounts/doctor_profile.html', {'page_user':user,
                                                                   'calendar':calendar_dict,
                                                                   'visiting_time_form':VisitingTimeForm()})
        else:
            return render(request,'accounts/client_profile.html', {'page_user':user})
    return render(request, 'accounts/banned_user.html', {'page_user':user})

class UpdateDoctorProfileView(LoginRequiredMixin, UpdateView):
    form_class = UpdateDoctorProfileForm
    template_name = 'accounts/update_profile.html'

    def get_object(self, queryset=None):
        return self.request.user.doctor

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_doctor:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username':self.request.user.username})

class UpdateClientProfileView(LoginRequiredMixin, UpdateView):
    form_class = UpdateUserProfileForm
    template_name = 'accounts/update_profile.html'

    def get_object(self, queryset=None):
        if not self.request.user.is_doctor:
            return self.request.user
        else:
            raise Http404

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username':self.request.user.username})

def ban_user_view(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_superuser:
        if user.is_superuser:
            title = 'Вы не имеете права блокировать администраторов'
            return render(request, 'errors/some_error.html', {'title': title})
        user.is_banned = True
        user.save()
        return redirect('accounts:profile', user.username)
    else:
        raise Http404

def unban_user_view(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_superuser:
        if user.is_superuser:
            title = 'Вы не можете разблокировать администратора'
            return render(request, 'errors/some_error.html', {'title': title})
        user.is_banned = False
        user.save()
        return redirect('accounts:profile', user.username)
    else:
        raise Http404

@require_clients
def buy_premium_account(request):
    user = request.user
    if request.method == 'POST':
        if user.balance.balance >= 50:
            with transaction.atomic():
                user.balance.balance -= 50
                user.client.is_premium = True
                user.client.save()
                user.balance.save()
            return redirect('accounts:profile', username=request.user.username)
        title = 'У вас недостаточно средсв для покупки'
        return render(request, 'errors/some_error.html', {'title':title})
    return render(request, 'accounts/buy_premium_account.html')

