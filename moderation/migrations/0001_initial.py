# Generated by Django 4.0.2 on 2023-05-10 16:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('doctors', '0001_initial'),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificationConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmation', to='doctors.doctor', verbose_name='Доктор')),
                ('qualifications', models.ManyToManyField(to='doctors.Qualification', verbose_name='Запрос на получение квалификации')),
            ],
            options={
                'verbose_name': 'Подтверждение Сертификации',
                'verbose_name_plural': 'Подтверждения Сертификаций',
            },
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cause', models.CharField(max_length=150, verbose_name='Причина')),
                ('accused', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accused_complaints', to=settings.AUTH_USER_MODEL, verbose_name='Обвиняемый')),
                ('initiator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='initiator_complaints', to=settings.AUTH_USER_MODEL, verbose_name='Инициатор')),
                ('ordered_call', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='chat.orderedcall', verbose_name='Звонок')),
            ],
            options={
                'verbose_name': 'Жалоба',
                'verbose_name_plural': 'Жалобы',
            },
        ),
        migrations.CreateModel(
            name='CertificationPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos/certifications', verbose_name='Фото сертификации')),
                ('certification_confirmation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moderation.certificationconfirmation', verbose_name='Подтверждение конфигураций')),
            ],
            options={
                'verbose_name': 'Фото Сертификации',
                'verbose_name_plural': 'Фотографии Сертификаций',
            },
        ),
    ]
