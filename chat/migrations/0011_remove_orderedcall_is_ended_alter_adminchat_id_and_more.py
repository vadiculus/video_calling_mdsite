# Generated by Django 4.0.2 on 2023-05-11 20:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_orderedcall_is_ended_alter_adminchat_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderedcall',
            name='is_ended',
        ),
        migrations.AlterField(
            model_name='adminchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('206eabe3-cb71-4e02-868f-42290a88345d'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='premiumchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('1b203739-aab7-450c-ab32-3c71429d372f'), primary_key=True, serialize=False),
        ),
    ]
