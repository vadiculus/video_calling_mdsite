from django.db import models
from accounts.models import Client

class Balance(models.Model):
    client = models.OneToOneField(Client, related_name='balance', on_delete=models.CASCADE, verbose_name='Клиент')
    balance = models.FloatField(default=0.00, verbose_name='Баланс')
