from django.db import models
from django.contrib.postgres.fields import ArrayField
from doctors.models import Doctor

class VisitingTime(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='Время приема')
    time = models.DateTimeField()
    is_booked = models.BooleanField(default=False, blank=True, verbose_name='Забронировано')

