from django.db import models
from accounts.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from accounts.models import Client
from django.core.validators import MaxValueValidator

class Qualification(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Квалификация'
        verbose_name_plural = 'Квалификации'

class Doctor(models.Model):
    user = models.OneToOneField(User, related_name='doctor', on_delete=models.CASCADE, verbose_name='Пользователь')
    is_confirmed = models.BooleanField(default=False, blank=True, verbose_name='Подтвержден')
    qualifications = models.ManyToManyField(Qualification, related_name='doctors', verbose_name='Квалификации')
    bio = models.TextField(blank=True, null=True,verbose_name='Биография')
    service_cost = models.DecimalField(max_digits=8, decimal_places=2,verbose_name='Стоимость услуг')
    rating = models.FloatField(null=True,blank=True,validators=[MaxValueValidator(5)],verbose_name='Рейтинг')

    def __str__(self):
        return self.user.full_name

    def username(self):
        return self.user.username

    class Meta:
        verbose_name = 'Доктор'
        verbose_name_plural = 'Доктора'

class Review(models.Model):
    rating = models.PositiveIntegerField(blank=True,
                                         null=True,
                                         validators=[MaxValueValidator(5), MinValueValidator(1)],
                                         verbose_name='Оценка')

    client = models.ForeignKey(Client, null=True, on_delete=models.PROTECT, verbose_name='Клиент')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews', verbose_name='Доктор')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

