from django.shortcuts import render
from django.views.generic import ListView
from doctors.models import Doctor
from .forms import DoctorSearchForm
from django.db.models import Q

def index(request):
    return render(request, 'doctors/index.html')

class DoctorSearchView(ListView):
    queryset = Doctor
    template_name = 'doctors/doctor_search_page.html'

    def get_queryset(self, *args, **kwargs):
        rating =self.request.GET.get('rating') if self.request.GET.get('rating') else 0
        qualifications = self.request.GET.get('qualifications') if self.request.GET.get('qualifications') else []
        if not (rating or qualifications):
            return []
        if self.request.user.is_superuser:
            queryset = Doctor.objects.select_related('user')\
                .filter(Q(rating=rating) | Q(qualifications__in= qualifications))
        else:
            queryset = Doctor.objects.select_related('user')\
                .filter(Q(user__is_banned=False) & Q(rating=rating) | Q(qualifications__in=qualifications))
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = DoctorSearchForm()
        return context


