from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    is_doctor = models.BooleanField(default=False, blank=True)
    photo = models.ImageField(upload_to='photos/clients', null=True, blank=True, verbose_name='Фото')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Client(models.Model):
    user = models.OneToOneField(User, related_name='client', on_delete=models.CASCADE, verbose_name='Пользователь')
    is_premium = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
