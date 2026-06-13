from django.urls import path
from django.contrib.auth import views as auth_views

from .views import login_view, register_view, logout_view, profile_view, forgot_password_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/login/',
        ),
        name='password_reset_confirm',
    ),
]
