from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'calendars'

urlpatterns = [
    path('book-a-call/<int:pk>', views.book_call_view, name='book_call'),
    path('create-visiting-time/', views.create_visiting_time_model, name='create_visiting_time')
]
