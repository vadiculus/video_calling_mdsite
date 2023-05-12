from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'calendars'

urlpatterns = [
    path('book-a-call/<int:pk>/', views.book_call_view, name='book_call'),
    path('create-visiting-time/', views.CreateVisitingTimeView.as_view(), name='create_visiting_time'),
]
