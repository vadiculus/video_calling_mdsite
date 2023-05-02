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
from accounts.models import User
from doctors.utils import require_doctors

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

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_doctor:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        qualifications = form.cleaned_data['qualifications']
        self.object = form.save(commit=False)
        self.object.doctor = self.request.user.doctor
        self.object.save()
        self.object.qualifications.set(qualifications)
        for image in self.request.FILES.getlist('certification_photos'):
            CertificationPhoto.objects.create(certification_confirmation=self.object, photo=image)

        return HttpResponseRedirect(self.get_success_url())





