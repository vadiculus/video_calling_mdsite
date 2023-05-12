from django.db import models
from django.contrib.postgres.fields import ArrayField
from doctors.models import Doctor
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

class VisitingTime(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='visiting_time', on_delete=models.CASCADE, verbose_name='Доктор')
    time = models.DateTimeField()
    is_booked = models.BooleanField(default=False, blank=True, verbose_name='Забронировано')
    max_time = models.IntegerField(default=60, validators=[MaxValueValidator(240), MinValueValidator(15)])
    time_end = models.DateTimeField(null=True, blank=True, verbose_name='Конечное время')

    def get_price(self):
        price = round((self.max_time / 60 * 100) * (float(self.doctor.service_cost) / 100))
        return price

    def get_percent(self):
        percent = self.get_price() / 100 * 5
        return percent

    def get_total_price(self):
        return self.get_price() + self.get_percent()

