from django.db import models
from doctors.models import Doctor
from accounts.models import Client
from calendars.models import VisitingTime
import uuid

class OrderedCall(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True)
    visiting_time = models.OneToOneField(VisitingTime,
                                         related_name='ordered_call',
                                         on_delete=models.CASCADE,
                                         verbose_name='Время визита')
    doctor = models.ForeignKey(Doctor, related_name='doctor_ordered_calls', on_delete=models.CASCADE, verbose_name='Доктор')
    client = models.ForeignKey(Client, related_name='client_ordered_calls', on_delete=models.CASCADE, verbose_name='Клиент')
    call_start = call_end = models.DateTimeField()
    call_end = models.DateTimeField(default=None, blank=True)
    is_success = models.BooleanField(default=False, verbose_name='Успешный')
