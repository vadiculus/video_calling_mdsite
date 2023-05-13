import decimal

from django.db import models
from calendars.models import VisitingTime
from django.core.validators import MaxValueValidator, MinValueValidator
from doctors.models import Doctor
from accounts.models import Client
from accounts.models import User
import datetime
from decimal import Decimal
from django.conf import settings
import pytz
import uuid
from mdsite.utils import server_tz
from django.db.models import Q
from django.db import transaction

from paynament.models import SiteBalance


class OrderedCall(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=True)
    visiting_time = models.OneToOneField(VisitingTime, null=True,
                                         related_name='ordered_call',
                                         on_delete=models.CASCADE,
                                         verbose_name='Время визита')
    participants = models.ManyToManyField(User, related_name='ordered_calls')
    ordered_time = models.IntegerField(
        default=60,
        validators=[MaxValueValidator(240)],
        verbose_name='Время звонка') # Выделеное время заказчика
    call_start = models.DateTimeField(null=True, blank=True)
    call_end = models.DateTimeField(null=True,default=None, blank=True)
    is_ended = models.BooleanField(default=False, verbose_name='Завершеный')
    is_success = models.BooleanField(default=False, verbose_name='Успешный')

    def is_active(self):
        visiting_time = self.visiting_time.time
        call_end = visiting_time + datetime.timedelta(
            minutes=self.visiting_time.max_time) - datetime.timedelta(minutes=10)
        utc = pytz.UTC
        # return visiting_time < utc.localize(datetime.datetime.now()) < call_end
        return True

    def transfer_money(self, client=None, doctor=None, site_balance=None):
        if not (client or doctor):
            doctor = self.get_doctor()
            client = self.get_client()
        doctor.balance.balance += self.get_price(doctor)
        client.balance.balance -= self.get_total_price(doctor, site_balance)
        doctor.balance.save()
        client.balance.save()

    def end_time(self):
        return str(self.visiting_time.time + datetime.timedelta(minutes=self.visiting_time.max_time))

    def get_price(self, doctor):
        '''Получает цену. Человек распалачивается не поминутно,
        а за каждый дополнительный отрезок времени'''
        doctor = doctor.doctor
        minutes_step = 20 # Отрезок времени
        minimal_percent = round(minutes_step / 60 * 100, 2) / 100 * round(float(doctor.service_cost), 2)
        if not self.call_start:
            raise Exception('OrderedCall has not "call_start"')
        time_difference = (self.call_start - self.call_end).total_seconds() / 60
        for timestamp_count in range(1, 7, round(minutes_step/10)):
            print(self.call_start, pytz.utc,  self.call_end)
            if time_difference > timestamp_count * minutes_step:
                continue
            else:
                if time_difference <= timestamp_count * minutes_step:
                    price = timestamp_count * minimal_percent
                else:
                    price = (timestamp_count + 1) * minimal_percent
                return Decimal(round(price, 2))

    def get_percent(self, doctor, site_balance):
        time_difference = (self.visiting_time.time_end - self.visiting_time.time).total_seconds() / 60
        percent = Decimal(time_difference / 60) * (Decimal(doctor.doctor.service_cost) / 100 * site_balance.percent)
        return Decimal(round(percent, 2))

    def get_total_price(self, doctor, site_balance):
        return round(self.get_price(doctor) + self.get_percent(doctor, site_balance), 2)

    def get_client(self):
        return self.participants.select_related('client', 'balance').get(is_doctor=False)

    def get_doctor(self):
        return self.participants.select_related('doctor', 'balance').get(is_doctor=True)

    def get_interlocutor(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def set_call_start(self, dt):
        self.call_start = datetime.datetime.now(server_tz)
        self.save()

class PremiumChat(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, editable=True)
    participants = models.ManyToManyField(User, related_name='premium_chats')

    def get_interlocutor(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4()
        return super().save(*args, **kwargs)

    def not_read_messages(self, user):
        return self.admin_messages.filter(~Q(author__user=user) & Q(read=False)).count()

class AdminChat(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, editable=True)
    participants = models.ManyToManyField(User, related_name='admin_chats')

    def get_interlocutor(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4()
        return super().save(*args, **kwargs)

    def not_read_messages(self, user):
        return self.admin_chat_messages.filter(~Q(author__user=User) & Q(read=False)).count()

class Message(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        abstract = True

class PremiumChatMessage(Message):
    author = models.ForeignKey(User, related_name='author_premium_messages', on_delete=models.PROTECT)
    chat = models.ForeignKey(PremiumChat, related_name='premium_chat_messages', on_delete=models.CASCADE)
    read = models.BooleanField(default=False, blank=True)

class AdminChatMessage(Message):
    author = models.ForeignKey(User, related_name='author_admin_messages', on_delete=models.PROTECT)
    chat = models.ForeignKey(AdminChat, related_name='admin_chat_messages', on_delete=models.CASCADE)
    read = models.BooleanField(default=False, blank=True)


