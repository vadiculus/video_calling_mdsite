# Generated by Django 4.0.2 on 2023-05-10 19:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_alter_adminchat_id_alter_premiumchat_id'),
        ('moderation', '0003_complaint_solved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='ordered_call',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ordered_call_complaint', to='chat.orderedcall', verbose_name='Звонок'),
        ),
    ]