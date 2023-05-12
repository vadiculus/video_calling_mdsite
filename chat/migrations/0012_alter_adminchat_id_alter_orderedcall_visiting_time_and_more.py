# Generated by Django 4.0.2 on 2023-05-11 21:08

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('calendars', '0003_visitingtime_max_time_alter_visitingtime_time_end'),
        ('chat', '0011_remove_orderedcall_is_ended_alter_adminchat_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('940cab2b-d14a-4371-8e5d-055775357207'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='orderedcall',
            name='visiting_time',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='ordered_call', to='calendars.visitingtime', verbose_name='Время визита'),
        ),
        migrations.AlterField(
            model_name='premiumchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('a6f9e367-9530-433b-858b-b1a8d7a67021'), primary_key=True, serialize=False),
        ),
    ]