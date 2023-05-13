from django.shortcuts import render
from doctors.models import Doctor
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from .models import CertificationConfirmation, CertificationPhoto, Complaint
from django.views.generic import CreateView
from .forms import AddCertificationConfirmationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from accounts.models import User
from doctors.utils import require_doctors
from django.urls import reverse_lazy
from chat.models import OrderedCall
from django.db import transaction
from django.shortcuts import redirect
from django.contrib.auth.models import Group, Permission
from .forms import ConflictCauseForm, CanselConfirmationCauseForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .tasks import send_mail, send_confirmation_mail
from chat.tasks import send_user_mail

from .utils import require_not_banned, require_staff

@require_staff
def сertification_сonfirmation_view(request, pk, status):
    '''Админы поттверждают или отвергают запрос на квалификацию врача'''
    if not status in ['confirmed', 'refusal']:
        raise Http404

    form = CanselConfirmationCauseForm

    if request.method == 'POST':
        form = CanselConfirmationCauseForm(request.POST)
        if form.is_valid():
            if status == 'refusal':
                with transaction.atomic():
                    confirmation = get_object_or_404(CertificationConfirmation.objects.select_related('doctor'), pk=pk)
                    doctor = confirmation.doctor
                    send_confirmation_mail.delay(email=doctor.user.email,
                                                      status='refusal',
                                                      cause=form.cleaned_data['cause'])
                    confirmation.delete()
                return redirect('admin:index')
    if request.method == 'GET':
        if status == 'refusal':
            return render(request, 'moderation/cansel_confirmation.html', {'form': form})
        if status == 'confirmed':
            with transaction.atomic():
                confirmation = get_object_or_404(CertificationConfirmation.objects.select_related('doctor'), pk=pk)

                doctor = confirmation.doctor

                doctor.is_confirmed = True
                doctor.qualifications.set(confirmation.qualifications.all())
                confirmation.delete()
                doctor.save()
                send_confirmation_mail.delay(email=doctor.user.email, status='confirmed')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class AddCertificationConfirmationView(CreateView):
    '''Класс для добавления квалификаций врачу. (Не создание профиля)'''
    form_class = AddCertificationConfirmationForm
    template_name = 'moderation/add_qualifications.html'
    success_url = reverse_lazy('accounts:doctor_success_register_message')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_doctor or request.user.is_banned:
                raise Http404
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user,**self.get_form_kwargs())

    def form_valid(self, form):
        qualifications = form.cleaned_data['qualifications']
        self.object = form.save(commit=False)
        self.object.doctor = self.request.user.doctor
        self.object.save()
        self.object.qualifications.set(qualifications)
        for image in self.request.FILES.getlist('certification_photos'):
            CertificationPhoto.objects.create(certification_confirmation=self.object, photo=image)

        return HttpResponseRedirect(self.get_success_url())

def complaint_info(request, status):
    body = 'В ближайшее время вам напишет администрация сайта чтобы решить вашу проблему'
    if status == 'accused':
        title = 'На вас была подана жалоба'
        return render(request, 'errors/text_page.html', {'title': title, 'body': body})
    elif status == 'initiator':
        title = 'Жалоба была успешно подана'
        return render(request, 'errors/text_page.html', {'title': title, 'body':body})
    else:
        pass
        # raise Http404

@require_staff
def conflict_resolution(request, pk, res_type):
    '''Решение вопроса жалобы'''

    complaint = get_object_or_404(Complaint.objects.prefetch_related('initiator', 'accused'), pk=pk)
    form = ConflictCauseForm
    initiator, accused = complaint.initiator, complaint.accused

    client, doctor = (initiator, accused) if not initiator.is_doctor else (accused, initiator)

    if not res_type in ['transfer-money', 'refusal']:
        raise Http404

    if request.method == 'POST':
        form = ConflictCauseForm(request.POST)
        if form.is_valid():
            title = 'Решение проблемы'
            if res_type == 'transfer-money':
                with transaction.atomic():
                    client.balance.balance -= complaint.price
                    doctor.balance.balance += complaint.price
                    client.balance.save(), doctor.balance.save()
                    if not initiator.is_doctor:
                        doctor_message = f'Ваша проблема по поводу жлобы была решена. На ваш счет было переведено {complaint.price} фантиков.'
                        client_message = f'Ваша жалоба была отклонена по причине: {form.cleaned_data["cause"]}'
                        send_user_mail(doctor.email, title, doctor_message)
                        send_user_mail(client.email, title, client_message)
                    complaint.delete()
                return redirect('admin:index')
            else:
                with transaction.atomic():
                    doctor_message = f'Вам не вернули деньги по причине: {form.cleaned_data["cause"]}'
                    client_message = f'Ваша проблема по поводу жалобы решена.'
                    send_user_mail(doctor.email, title, doctor_message)
                    send_user_mail(client.email, title, client_message)
                    complaint.delete()
                return redirect('admin:index')
    return render(request, 'moderation/conflict_resolution.html', {'form': form})

def make_user_admin(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_superuser:
        user.is_staff = True
        user.save()
        return redirect('accounts:profile', username)
    raise Http404