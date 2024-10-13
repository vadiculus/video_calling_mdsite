import datetime

from django.db.models import Q
from django.db.models.functions import TruncDay
from django.shortcuts import render
from chat.models import OrderedCall
from django.views.decorators.http import require_POST
from chat.forms import CreateCallForm
from django.shortcuts import get_object_or_404, redirect, reverse
from calendars.models import VisitingTime
from moderation.utils import require_not_banned
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
from django.contrib.auth.views import login_required

@login_required

@require_not_banned
def book_call_view(request, pk):
    visiting_time = get_object_or_404(VisitingTime.objects.select_related('doctor',
                                                                          'doctor__user',
                                                                          'doctor__user__balance'), pk=pk)
    ordered_calls = OrderedCall.objects.select_related('visiting_time').prefetch_related('participants')\
        .filter(participants=request.user)

    total_price_ordered_calls = sum([call.visiting_time.get_total_price() for call in ordered_calls])

    if request.user == visiting_time.doctor.user:
        return redirect('calendars:delete_visiting_time', pk=visiting_time.id)

    if not visiting_time.is_booked:
        if request.user.is_staff or request.user.is_superuser:
            raise Http404

        balance = request.user.balance.balance

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = self.request.user.doctor.visiting_time.filter(time__gt=datetime.datetime.utcnow()).annotate(day=TruncDay('time'))\
                    .values('day','id', 'time','time_end', 'is_booked')
        calendar_dict = {}
        for day in calendar:
            if str(day['day']) in calendar_dict:
                calendar_dict[str(day['day'])].append({'id': day['id'], 'time': str(day['time']),
                                                       'time_end': str(day['time_end']), 'is_booked': day['is_booked']})
            else:
                calendar_dict[str(day['day'])] = [{'id': day['id'], 'time': str(day['time']),
                                                   'time_end': str(day['time_end']), 'is_booked': day['is_booked']}]
        context['calendar'] = calendar_dict
        return context

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
                                                       minutes=self.object.max_time)) &
                                               Q(ordered_call__is_ended=False))

        if not visiting_times:
            self.object.doctor = self.request.user.doctor
            self.object.time_end = self.object.time + datetime.timedelta(minutes=self.object.max_time)
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            error_text = 'You already have calls for this scheduled time'
            return render(self.request, 'calendars/add_visiting_time.html', {'form':form,
                                                                             'errors':[error_text]})

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username':self.request.user.username})

def delete_visiting_time(request, pk):
    visiting_time = get_object_or_404(VisitingTime.objects.select_related('ordered_call', 'doctor__user'), pk=pk)

    if request.method == 'POST':
        if request.user == visiting_time.doctor.user:
            if not visiting_time.is_booked:
                visiting_time.delete()
            else:
                message_body = f'Dr. {visiting_time.doctor.user.full_name} canceled the scheduled call'
                send_user_mail.delay(visiting_time.ordered_call.get_client().email, 'Conference cancellation', message_body)
                visiting_time.delete()
            return redirect('accounts:profile', request.user.username)
        else:
            raise Http404
    else:
        return render(request, 'calendars/delete_visiting_time.html')

