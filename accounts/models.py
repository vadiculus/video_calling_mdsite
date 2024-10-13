from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

class User(AbstractUser):
    full_name = models.CharField(max_length=150, verbose_name='Full name')
    is_doctor = models.BooleanField(default=False, blank=True)
    photo = models.ImageField(upload_to='photos/clients', null=True, blank=True, verbose_name='Foto')
    is_banned = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Client(models.Model):
    user = models.OneToOneField(User, related_name='client', on_delete=models.CASCADE, verbose_name='User')
    is_premium = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
