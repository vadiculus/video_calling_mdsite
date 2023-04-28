from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'moderation'

urlpatterns = [
    path('confirmation/<int:pk>/<str:status>', views.сertification_сonfirmation_view, name='confirmation'),
]
