from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'moderation'

urlpatterns = [
    path('confirmation/<int:pk>/<str:status>', views.сertification_сonfirmation_view, name='confirmation'),
    path('complaint-info/<str:status>/', views.complaint_info, name='complaint_info'),
    path('conflict-resolution/<int:pk>/<str:res_type>/', views.conflict_resolution, name='conflict_resolution'),
    path('make-user-admin/<str:username>/', views.make_user_admin, name='make_user_admin'),
    path('create-complaint/<str:username>/', views.CreateStandardComplaint.as_view(), name='create_complaint'),
]
