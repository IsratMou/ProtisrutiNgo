from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login-options/', views.LoginOptionsView.as_view(), name='login_options'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login-redirect/', views.login_redirect_view, name='login_redirect'),
    path('register/user/', views.register_user_view, name='register_user'),
    path('register/counselor/', views.register_counselor_view, name='register_counselor'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('counselor-dashboard/', views.counselor_dashboard, name='counselor_dashboard'),
    path('donation/', views.donation_view, name='donation'),
]