from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/client/', views.RegisterClientView.as_view(), name='register_client'),
    path('register/doctor/', views.RegisterDoctorUserView.as_view(), name='register_doctor'),
    path('register/certification-confirmation/', views.CertificationConfirmationView.as_view(), name='certification_confirmation'),
    path('register/мessage_for_registered_doctor', views.doctor_success_register_message, name='doctor_success_register_message'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('update-doctor-profile/', views.UpdateDoctorProfileView.as_view(), name='update_doctor_profile'),
    path('update-client-profile/', views.UpdateClientProfileView.as_view(), name='update_client_profile'),
    path('change-password/', views.PasswordChangeView.as_view(
            template_name='accounts/change_password.html',
            success_url=views.reverse_lazy('accounts:login')),
        name='change_password'),
    path('add-certification-confirmation/', views.AddCertificationConfirmationView.as_view(),
         name='add_certification_confirmation'),
    path('ban/<str:username>', views.ban_user_view, name='ban'),
    path('unban/<str:username>', views.unban_user_view, name='unban'),
    path('buy-premium-account/', views.buy_premium_account, name='buy_premium_account')

]
