# Generated by Django 4.0.2 on 2023-05-17 01:59

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('calendars', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminChat',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('6a560e2e-27ce-42c6-9ace-b390caeb2318'), primary_key=True, serialize=False)),
                ('participants', models.ManyToManyField(related_name='admin_chats', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PremiumChat',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('d2d9bd24-d5be-4dca-beab-eb9d18603044'), primary_key=True, serialize=False)),
                ('participants', models.ManyToManyField(related_name='premium_chats', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PremiumChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('read', models.BooleanField(blank=True, default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='author_premium_messages', to=settings.AUTH_USER_MODEL)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='premium_chat_messages', to='chat.premiumchat')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderedCall',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('ordered_time', models.IntegerField(default=60, validators=[django.core.validators.MaxValueValidator(240)], verbose_name='Время звонка')),
                ('call_start', models.DateTimeField(blank=True, null=True)),
                ('call_end', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_ended', models.BooleanField(default=False, verbose_name='Завершеный')),
                ('have_complaint', models.BooleanField(default=False)),
                ('participants', models.ManyToManyField(related_name='ordered_calls', to=settings.AUTH_USER_MODEL)),
                ('visiting_time', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_call', to='calendars.visitingtime', verbose_name='Время визита')),
            ],
        ),
        migrations.CreateModel(
            name='AdminChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('read', models.BooleanField(blank=True, default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='author_admin_messages', to=settings.AUTH_USER_MODEL)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_chat_messages', to='chat.adminchat')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
