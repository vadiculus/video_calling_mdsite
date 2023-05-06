from django.shortcuts import render
from chat.models import OrderedCall
from django.views.decorators.http import require_POST
from chat.forms import CreateCallForm
from django.shortcuts import get_object_or_404, redirect, reverse
from calendars.models import VisitingTime
from .forms import VisitingTimeForm
from doctors.utils import require_clients
from django.db import transaction
from django.views.generic import CreateView
from doctors.utils import require_doctors
from django.urls import reverse_lazy
from django.http import Http404, HttpResponseRedirect

@require_clients
def book_call_view(request, pk):
    visiting_time = get_object_or_404(VisitingTime, pk=pk)
    form = CreateCallForm(max_time=visiting_time.max_time)
    if not visiting_time.is_booked:
        if request.method == 'POST':
            call_form = CreateCallForm(data=request.POST)
            if call_form.is_valid():
                with transaction.atomic():
                    call_form.save(request.user, visiting_time, commit=True)
                return redirect('doctors:index')
        return render(request, 'calendars/book_call.html', {'form':form, 'visiting_time':visiting_time})
    else:
        return render(request, 'calendars/booked_error.html')

class CreateVisitingTimeView(CreateView):
    form_class = VisitingTimeForm
    template_name = 'calendars/add_visiting_time.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_doctor:
            return super().dispatch(request, *args, **kwargs)
        raise Http404

    def form_valid(self, form):
        self.object = form.save(commit=False)
        visiting_times = VisitingTime.objects.filter(doctor=self.request.user.doctor, time=self.object.time)
        if not visiting_times:
            self.object.doctor = self.request.user.doctor
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username':self.request.user.username})

