from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import ListView
from doctors.models import Doctor, Review
from .forms import DoctorSearchForm
from django.db.models import Q
from moderation.tasks import send_confirmation_mail
from django.conf import settings
from django.views.generic import CreateView
from .forms import ReviewForm
from django.shortcuts import get_object_or_404
from accounts.models import User
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from .utils import require_not_superusers
from chat.tasks import send_user_mail

def index(request):
    queryset = Doctor.objects.select_related('user') \
        .filter(user__is_banned=False).order_by('-rating')[:10]
    return render(request, 'doctors/index.html', {'doctors': queryset, 'form':DoctorSearchForm})

class DoctorSearchView(ListView):
    queryset = Doctor
    template_name = 'doctors/doctor_search_page.html'

    def get_queryset(self, *args, **kwargs):
        rating =self.request.GET.get('rating') if self.request.GET.get('rating') else 0
        qualifications = self.request.GET.get('qualifications') if self.request.GET.get('qualifications') else []
        if not (rating or qualifications):
            return []
        if self.request.user.is_staff:
            queryset = Doctor.objects.select_related('user')\
                .filter(Q(rating__gte=rating) | Q(qualifications__in= qualifications))
        else:
            queryset = Doctor.objects.select_related('user')\
                .filter(Q(is_confirmed=True) & Q(user__is_banned=False) & Q(rating__gte=rating) | Q(qualifications__in=qualifications))
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = DoctorSearchForm(self.request.GET)
        return context

class CreateReview(CreateView):
    form_class = ReviewForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_doctor and not request.user.is_staff:
                return super().dispatch(request, *args, **kwargs)
        raise Http404

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username': self.user_doctor.username})

    def form_valid(self, form):
        username = self.kwargs.get('username')
        self.user_doctor = get_object_or_404(User.objects.select_related('doctor'), username=username)
        reviews = Review.objects.filter(doctor=self.user_doctor.doctor, client=self.request.user.client)

        if reviews:
            reviews.delete()
        self.object = Review.objects.create(doctor=self.user_doctor.doctor,
                                                client=self.request.user.client,
                                                **form.cleaned_data)
        return HttpResponseRedirect(self.get_success_url())


