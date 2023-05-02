from django.db import models
from calendars.models import VisitingTime
from django.core.validators import MaxValueValidator, MinValueValidator
from doctors.models import Doctor
from accounts.models import Client
from accounts.models import User
import uuid

class OrderedCall(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, editable=True)
    visiting_time = models.OneToOneField(VisitingTime,
                                         related_name='ordered_call',
                                         on_delete=models.CASCADE,
                                         verbose_name='Время визита')
    doctor = models.ForeignKey(Doctor, related_name='doctor_ordered_calls', on_delete=models.CASCADE, verbose_name='Доктор')
    client = models.ForeignKey(Client, related_name='client_ordered_calls', on_delete=models.CASCADE, verbose_name='Клиент')
    ordered_time = models.IntegerField(
        default=60,
        validators=[MaxValueValidator(240), MinValueValidator(15)],
        verbose_name='Время звонка') # Выделеное время заказчика
    call_start = call_end = models.DateTimeField()
    call_end = models.DateTimeField(null=True,default=None, blank=True)
    is_success = models.BooleanField(default=False, verbose_name='Успешный')

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4()
        return super().save(*args, **kwargs)

class PremiumChat(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, editable=True)
    participants = models.ManyToManyField(User, related_name='premium_chats')

    def get_interlocutor(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4()
        return super().save(*args, **kwargs)

class AdminChat(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, editable=True)
    participants = models.ManyToManyField(User, related_name='admin_chats')

    def get_interlocutor(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4()
        return super().save(*args, **kwargs)

class Message(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        abstract = True

class PremiumChatMessage(Message):
    author = models.ForeignKey(User, related_name='author_premium_messages', on_delete=models.PROTECT)
    chat = models.ForeignKey(PremiumChat, related_name='premium_chat_messages', on_delete=models.CASCADE)

class AdminChatMessage(Message):
    author = models.ForeignKey(User, related_name='author_admin_messages', on_delete=models.PROTECT)
    chat = models.ForeignKey(AdminChat, related_name='admin_chat_messages', on_delete=models.CASCADE)


