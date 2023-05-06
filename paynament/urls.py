from django.urls import path
from . import views

app_name = 'paynament'

urlpatterns = [
    path('top-up-balance/', views.top_up_balance, name='top_up_balance')
]