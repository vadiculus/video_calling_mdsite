from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('premium-chat/<uuid:chat_id>/', views.premium_chat, name='premium_chat'),
    path('administration-chat/<uuid:chat_id>/', views.admin_chat, name='admin_chat'),
    path('create-chat/<str:username>', views.create_chat, name='create_chat'),
    path('premium-chat-list/', views.premium_chat_list_view, name='premium_chat_list'),
    path('administration-chat-list/', views.admin_chat_list_view, name='admin_chat_list'),
    path('ordered-call/<uuid:pk>/', views.ordered_call_view, name='ordered_call'),
    path('calendar/ordered_calls/', views.ordered_call_list, name='ordered_call_list')
]