import datetime

from django.db.models import Q
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
import pytz
from mdsite.utils import server_tz
from chat.tasks import send_user_mail

@require_clients
def book_call_view(request, pk):
    visiting_time = get_object_or_404(VisitingTime.objects.select_related('doctor',
                                                                          'doctor__user',
                                                                          'doctor__user__balance'), pk=pk)
    ordered_calls = OrderedCall.objects.select_related('visiting_time').prefetch_related('participants')\
        .filter(participants=request.user, is_success=False)

    total_price_ordered_calls = sum([call.visiting_time.get_total_price() for call in ordered_calls])

    balance = request.user.balance.balance

    if not visiting_time.is_booked:
        if request.user.is_superuser:
            raise Http404

        if request.method == 'POST':
            if balance < total_price_ordered_calls + visiting_time.get_total_price():
                print(total_price_ordered_calls + visiting_time.get_total_price())
                return render(request, 'calendars/book_call.html', {'visiting_time': visiting_time,
                                                                    'errors': ['У вас есть другие неоплаченые звонки. Пополните счет.']})
            if balance > visiting_time.get_total_price():
                with transaction.atomic():
                    call = OrderedCall()
                    call.visiting_time = visiting_time
                    visiting_time.is_booked=True
                    visiting_time.save()
                    call.save()
                    call.participants.set([visiting_time.doctor.user, request.user])
                    return redirect('doctors:index')
            else:
                return render(request, 'calendars/book_call.html', {'visiting_time':visiting_time,
                                                                    'errors':['У вас недостаточно денег на счету']})
        return render(request, 'calendars/book_call.html', {'visiting_time':visiting_time})
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
        '''Тут время переводится из дефолтного UTC выданного формой в часовой пояс клиента, а потом переводится в utc'''
        self.object = form.save(commit=False)
        timezone = pytz.timezone(form.cleaned_data['timezone'])
        dt_timezone = timezone.normalize(timezone.localize(
            datetime.datetime.combine(self.object.time.date(), datetime.time.min) + datetime.timedelta(
                hours=self.object.time.hour,
                minutes=self.object.time.minute)))
        self.object.time = dt_timezone.astimezone(server_tz)

        visiting_times = VisitingTime.objects.filter(doctor=self.request.user.doctor) #Отфильровать по доктору

        visiting_times = visiting_times.filter(Q(time__gte=self.object.time, #По времени
                                                   time__lte=self.object.time + datetime.timedelta(
                                                       minutes=self.object.max_time)) |
                                                 Q(time_end__gt=self.object.time ,
                                                   time_end__lte=self.object.time + datetime.timedelta(
                                                       minutes=self.object.max_time)))

        if not visiting_times:
            self.object.doctor = self.request.user.doctor
            self.object.time_end = self.object.time + datetime.timedelta(minutes=self.object.max_time)
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            error_text = 'У вас уже есть звонки на это назначенное время'
            return render(self.request, 'calendars/add_visiting_time.html', {'form':form,
                                                                             'errors':[error_text]})

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username':self.request.user.username})

