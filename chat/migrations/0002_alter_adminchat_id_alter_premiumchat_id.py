# Generated by Django 4.0.2 on 2023-05-20 14:37

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
            field=models.UUIDField(default=uuid.UUID('dc8b6e85-12e2-472e-afd2-5bf1215fbd53'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='premiumchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c9204e5e-7f4e-4eb4-be6e-92879be5ee54'), primary_key=True, serialize=False),
        ),
    ]
