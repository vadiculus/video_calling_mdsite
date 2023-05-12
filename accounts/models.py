from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

class User(AbstractUser):
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    is_doctor = models.BooleanField(default=False, blank=True)
    photo = models.ImageField(upload_to='photos/clients', null=True, blank=True, verbose_name='Фото')
    is_banned = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Client(models.Model):
    user = models.OneToOneField(User, related_name='client', on_delete=models.CASCADE, verbose_name='Пользователь')
    is_premium = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class SiteMessage(models.Model):
    message = models.TextField()
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    read = models.BooleanField(default=False, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
