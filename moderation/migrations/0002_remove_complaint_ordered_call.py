# Generated by Django 4.0.2 on 2023-05-13 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaint',
            name='ordered_call',
        ),
    ]