from django.urls import path
from . import views

app_name = 'paynament'

urlpatterns = [
    path('top-up-balance/', views.top_up_balance, name='top_up_balance'),
    path('site-balance/', views.SiteBalanceUpdateView.as_view(), name='site_balance'),
]