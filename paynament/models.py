from django.db import models
from accounts.models import User

class Balance(models.Model):
    user = models.OneToOneField(User, related_name='balance', on_delete=models.CASCADE, verbose_name='Клиент')
    balance = models.DecimalField(decimal_places=2, max_digits=8,default=0.00, verbose_name='Баланс')
