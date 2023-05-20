import datetime
from django.db import models
from doctors.models import Doctor
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from paynament.models import SiteBalance

class VisitingTime(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='visiting_time', on_delete=models.CASCADE, verbose_name='Доктор')
    time = models.DateTimeField()
    is_booked = models.BooleanField(default=False, blank=True, verbose_name='Забронировано')
    max_time = models.IntegerField(default=60, validators=[MaxValueValidator(240), MinValueValidator(20)])
    time_end = models.DateTimeField(null=True, blank=True, verbose_name='Конечное время')

    def get_price(self):
        price = round((self.max_time / 60 * 100) * (float(self.doctor.service_cost) / 100))
        return price

    def get_percent(self):
        site_balance = SiteBalance.objects.get(pk=1)
        time_difference = (self.time_end - self.time).total_seconds() / 60
        percent = self.doctor.service_cost / 100 * float(site_balance.percent) * time_difference / 60
        return round(percent, 2)

    def get_total_price(self):
        print(self.get_percent())
        return round(self.get_price() + self.get_percent(), 2)

