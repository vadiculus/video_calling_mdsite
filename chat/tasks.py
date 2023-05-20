import datetime

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from calendars.models import VisitingTime
from mdsite.celery import app


@app.task
def send_user_mail(email, title, body):
    message_html = render_to_string('moderation/email.html', {'title': title,
                                                              'body': body})
    send_mail('Подтверждение сертификации',
              '',
              settings.EMAIL_HOST_USER,
              [email],
              html_message=message_html,
              fail_silently=False)

@app.task
def delete_old_visiting_time():
    from chat.models import OrderedCall
    visiting_times = VisitingTime.objects.select_related('ordered_call').filter(time_end__lt=datetime.datetime.utcnow())
    for visiting_time in visiting_times:
        if not visiting_time.is_booked:
            visiting_time.delete()
            continue

        try:
            if visiting_time.ordedred_call.is_ended:
                if not visiting_time.ordedred_call.have_complaint:
                    visiting_time.ordered_call.transfer_money()
                    continue
            else:
                if visiting_time.ordered_call.call_start:
                    visiting_time.ordered_call.transfer_money()
                else:
                    visiting_time.ordered_call.transfer_money(half_sum=True)

        except OrderedCall.DoesNotExist:
            visiting_time.delete()
            continue
        except AttributeError:
            visiting_time.delete()
            continue
