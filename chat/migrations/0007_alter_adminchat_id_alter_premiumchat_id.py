# Generated by Django 4.0.2 on 2023-05-10 19:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_alter_adminchat_id_alter_premiumchat_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('552b928c-8407-4794-bdd5-1c55f8600824'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='premiumchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('6beb6763-4902-40da-991f-93aaf7a11881'), primary_key=True, serialize=False),
        ),
    ]