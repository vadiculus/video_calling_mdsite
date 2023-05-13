from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

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
    pass