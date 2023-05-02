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

@require_clients
def book_call_view(request, pk):
    visiting_time = get_object_or_404(VisitingTime, pk=pk)
    form = CreateCallForm(max_time=visiting_time.max_time)
    if not visiting_time.is_booked:
        if request.method == 'POST':
            call_form = CreateCallForm(data=request.POST)
            if call_form.is_valid():
                with transaction.atomic():
                    call_form.save(request.user.client, visiting_time, commit=True)
                return redirect('doctors:index')
        return render(request, 'calendars/book_call.html', {'form':form, 'visiting_time':visiting_time})
    else:
        return render(request, 'calendars/booked_error.html')

@require_POST
@require_doctors
def create_visiting_time_model(request):
    form = VisitingTimeForm(request.POST)
    if form.is_valid():
        visiting_time = form.save(commit=False)
        visiting_times = VisitingTime.objects.filter(doctor=request.user.doctor, time=visiting_time.time)
        if not visiting_times:
            visiting_time.doctor = request.user.doctor
            visiting_time.save()
            return redirect('accounts:profile', request.user.username)
        title = 'У вас уже есть запись на это время'
        return render(request, 'errors/some_error.html', {'title': title})
    return render(request, 'errors/some_error.html', {'title':form.errors})


