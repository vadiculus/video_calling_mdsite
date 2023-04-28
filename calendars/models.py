from django.db import models
from django.contrib.postgres.fields import ArrayField
from doctors.models import Doctor

class VisitingTime(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='visiting_time', on_delete=models.CASCADE, verbose_name='Доктор')
    time = models.DateTimeField()
    is_booked = models.BooleanField(default=False, blank=True, verbose_name='Забронировано')

