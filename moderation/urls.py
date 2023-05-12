from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'moderation'

urlpatterns = [
    path('confirmation/<int:pk>/<str:status>', views.сertification_сonfirmation_view, name='confirmation'),
    path('complaint-info/<str:status>/', views.complaint_info, name='complaint_info'),
    path('doctor-transfer-money/<uuid:pk>/', views.transfer_money, name='doctor_transfer_money'),
    path('make-user-admin/<str:username>/', views.make_user_admin, name='make_user_admin')
]
