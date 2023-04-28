# Generated by Django 4.0.2 on 2023-04-25 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorComplaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cause', models.CharField(max_length=150, verbose_name='Причина')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.client', verbose_name='Доктор')),
            ],
            options={
                'verbose_name': 'Жалоба на доктора',
                'verbose_name_plural': 'Жалобы на докторов',
            },
        ),
        migrations.CreateModel(
            name='ClientComplaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cause', models.CharField(max_length=150, verbose_name='Причина')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctors.doctor', verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'Жалоба на клиента',
                'verbose_name_plural': 'Жалобы на клиентов',
            },
        ),
        migrations.CreateModel(
            name='CertificationPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos/certifications', verbose_name='Фото сертификации')),
                ('certification_confirmation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctors.doctor', verbose_name='Подтверждение конфигураций')),
            ],
            options={
                'verbose_name': 'Фото Сертификации',
                'verbose_name_plural': 'Фотографии Сертификаций',
            },
        ),
        migrations.CreateModel(
            name='CertificationConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctors.doctor', verbose_name='Доктор')),
            ],
            options={
                'verbose_name': 'Подтверждение Сертификации',
                'verbose_name_plural': 'Подтверждения Сертификаций',
            },
        ),
    ]
