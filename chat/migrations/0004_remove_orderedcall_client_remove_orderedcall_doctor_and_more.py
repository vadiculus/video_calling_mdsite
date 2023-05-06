# Generated by Django 4.0.2 on 2023-05-05 21:59

from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0003_alter_adminchat_id_alter_orderedcall_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderedcall',
            name='client',
        ),
        migrations.RemoveField(
            model_name='orderedcall',
            name='doctor',
        ),
        migrations.AddField(
            model_name='orderedcall',
            name='participants',
            field=models.ManyToManyField(related_name='ordered_calls', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='adminchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('bac42c54-33a2-424c-9243-303bd352a8df'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='orderedcall',
            name='id',
            field=models.UUIDField(default=uuid.UUID('58e8d8ab-7f45-4cb3-a8bc-6c9e24b30039'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='premiumchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('0400235b-8e7d-4d91-9754-25f50db46c26'), primary_key=True, serialize=False),
        ),
    ]
