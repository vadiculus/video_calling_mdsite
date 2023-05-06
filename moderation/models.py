from django.db import models
from doctors.models import Doctor
from doctors.models import Qualification
from accounts.models import Client

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

class ClientComplaint(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    cause = models.CharField(max_length=150, verbose_name='Причина')

    class Meta:
        verbose_name = 'Жалоба на клиента'
        verbose_name_plural = 'Жалобы на клиентов'

class DoctorComplaint(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='Доктор')
    cause = models.CharField(max_length=150, verbose_name='Причина')

    class Meta:
        verbose_name = 'Жалоба на доктора'
        verbose_name_plural = 'Жалобы на докторов'
