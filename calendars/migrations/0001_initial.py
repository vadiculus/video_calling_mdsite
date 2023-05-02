# Generated by Django 4.0.2 on 2023-04-29 17:07

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitingTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('is_booked', models.BooleanField(blank=True, default=False, verbose_name='Забронировано')),
                ('max_time', models.IntegerField(default=60, validators=[django.core.validators.MaxValueValidator(240), django.core.validators.MinValueValidator(15)])),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visiting_time', to='doctors.doctor', verbose_name='Доктор')),
            ],
        ),
    ]
