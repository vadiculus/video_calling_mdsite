# Generated by Django 4.0.2 on 2023-05-13 19:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('6d66fa90-993e-4190-b092-c64d4de5ea92'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='premiumchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('6e618860-7bec-4e27-bd0e-606560fcf3f5'), primary_key=True, serialize=False),
        ),
    ]
