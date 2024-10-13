from django.db import models
from accounts.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from accounts.models import Client
from django.core.validators import MaxValueValidator
from django.db.models import Sum, Count
from django.db import transaction


class Qualification(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Qualification'
        verbose_name_plural = 'Qualifications'

class Doctor(models.Model):
    user = models.OneToOneField(User, related_name='doctor', on_delete=models.CASCADE, verbose_name='User')
    is_confirmed = models.BooleanField(default=False, blank=True, verbose_name='Сonfirmed')
    qualifications = models.ManyToManyField(Qualification, related_name='doctors', verbose_name='Qualifications')
    bio = models.TextField(blank=True, null=True,verbose_name='Biography')
    service_cost = models.PositiveIntegerField(verbose_name='Cost of services')
    rating = models.FloatField(null=True,blank=True,validators=[MaxValueValidator(5)],verbose_name='Rating')

    def __str__(self):
        return self.user.full_name

    def username(self):
        return self.user.username

    class Meta:
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

class Review(models.Model):
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)],
                                         verbose_name='Rating')

    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL, verbose_name='Client')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews', verbose_name='Doctor')
    review = models.TextField(null=True, blank=True, verbose_name='Review')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            reviews = Review.objects.filter(doctor=self.doctor).aggregate(
                total_rating=Sum('rating'),
                count = Count('id')
            )
            if reviews['count']:
                self.doctor.rating = reviews['total_rating'] / reviews['count']
            else:
                self.doctor.rating = self.rating
            self.doctor.save()
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('client', 'doctor')

