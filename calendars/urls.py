from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'calendars'

urlpatterns = [
    path('book-a-call/<int:pk>/', views.book_call_view, name='book_call'),
    path('create-visiting-time/', views.CreateVisitingTimeView.as_view(), name='create_visiting_time'),
    path('delete-visiting-time/<int:pk>/', views.delete_visiting_time, name='delete_visiting_time'),
]
