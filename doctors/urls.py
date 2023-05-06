from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.DoctorSearchView.as_view(), name='index'),
    path('doctor-search/', views.DoctorSearchView.as_view(), name='doctor_search')
]
