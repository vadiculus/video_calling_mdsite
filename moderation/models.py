from django.db import models
from doctors.models import Doctor
from doctors.models import Qualification
from accounts.models import Client, User
from chat.models import OrderedCall

class CertificationConfirmation(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='confirmation', on_delete=models.CASCADE, verbose_name='Доктор')
    qualifications = models.ManyToManyField(Qualification, verbose_name='Запрос на получение квалификации')

    def __str__(self):
        return f'Запрос на получение квалификации {self.id}'

    class Meta:
        verbose_name = 'Подтверждение Сертификации'
        verbose_name_plural = 'Подтверждения Сертификаций'

class CertificationPhoto(models.Model):
    certification_confirmation = models.ForeignKey(CertificationConfirmation, on_delete=models.CASCADE, verbose_name='Подтверждение конфигураций')
    photo = models.ImageField(upload_to='photos/certifications', null=True, blank=True, verbose_name='Фото сертификации')

    class Meta:
        verbose_name = 'Фото Сертификации'
        verbose_name_plural = 'Фотографии Сертификаций'

class Complaint(models.Model):
    accused = models.ForeignKey(User, related_name='accused_complaints', on_delete=models.CASCADE, verbose_name='Обвиняемый')
    initiator = models.ForeignKey(User, related_name='initiator_complaints', on_delete=models.PROTECT, verbose_name='Инициатор')
    cause = models.CharField(max_length=150, verbose_name='Причина')
    ordered_call = models.ForeignKey(OrderedCall, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Звонок')

    class Meta:
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'
