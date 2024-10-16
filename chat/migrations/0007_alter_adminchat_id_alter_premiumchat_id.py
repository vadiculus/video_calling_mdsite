# Generated by Django 4.0.2 on 2024-10-13 23:47

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
            field=models.UUIDField(default=uuid.UUID('7eaabcbd-a5ea-4ced-a584-99cbbfaf0bdd'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='premiumchat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c7dc1314-ea36-4f4f-a36b-3f2cc964d189'), primary_key=True, serialize=False),
        ),
    ]
