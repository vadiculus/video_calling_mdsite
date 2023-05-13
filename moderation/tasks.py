from django.core.mail import send_mail
from django.template.loader import render_to_string

from mdsite.celery import app
from django.conf import settings

@app.task
def send_confirmation_mail(email=None, status=None, cause=None):
    if status == 'confirmed':
        body = f'Теперь вам доступен полный функционал для работы. Удачи!'
        message_html = render_to_string('moderation/email.html', {'title': 'Вашу заявку приняли!',
                                                                  'body': body})
        send_mail('Подтверждение сертификации',
                  '',
                  settings.EMAIL_HOST_USER,
                  [email],
                  html_message=message_html,
                  fail_silently=False)
    else:
        body = f'Вашу заявку отклонили по причине: {cause}'
        message_html = render_to_string('moderation/email.html', {'title': 'Вашу заявку приняли!',
                                                                  'body': body})
        send_mail('Отклюнение проверки сертификации',
                  '',
                  settings.EMAIL_HOST_USER,
                  [email],
                  html_message=message_html,
                  fail_silently=False)