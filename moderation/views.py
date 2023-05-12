from django.shortcuts import render
from doctors.models import Doctor
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from .models import CertificationConfirmation, CertificationPhoto
from django.views.generic import CreateView
from .forms import AddCertificationConfirmationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from accounts.models import User, SiteMessage
from doctors.utils import require_doctors
from django.urls import reverse_lazy
from chat.models import OrderedCall
from django.db import transaction
from django.shortcuts import redirect

from .utils import require_not_banned


def сertification_сonfirmation_view(request, pk, status):
    '''Админы поттверждают или отвергают запрос на квалификацию врача'''
    if request.user.is_superuser:
        if status and pk:
            confirmation = get_object_or_404(CertificationConfirmation.objects.select_related('doctor'), pk=pk)

            doctor = confirmation.doctor

            doctor.is_confirmed = True
            doctor.qualifications.set(confirmation.qualifications.all())
            confirmation.delete()
            doctor.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            raise Http404
    raise PermissionDenied

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

def transfer_money(request, pk):
    '''Решение вопроса жалобы'''
    call = get_object_or_404(OrderedCall.objects.prefetch_related('participants'), pk=pk)
    if request.user.is_superuser:
        with transaction.atomic():
            call.transfer_money()
            call.ordered_call_complaint.solved = True
            doctor_message = f'Ваша проблема была решена. На ваш счет было переведено {round(call.get_price(), 2)} фантиков.'
            SiteMessage.objects.create(recipient=call.get_doctor(),
                                       message=doctor_message)
            call.ordered_call_complaint.save()
            call.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    raise Http404

def make_user_admin(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_superuser:
        user.is_superuser = True
        user.save()
        return redirect('accounts:profile', username)
    raise Http404