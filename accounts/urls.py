from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('settings/', views.account_settings_view, name='account-settings'),
    path('password/change/', views.AccountPasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', auth_views.PasswordResetView.as_view(
        form_class=StyledPasswordResetForm,
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy('password-reset-done'),
    ), name='password-reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password-reset-done'),
    path('password/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        form_class=StyledSetPasswordForm,
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('password-reset-complete'),
    ), name='password-reset-confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password-reset-complete'),
    path('users/', views.user_list_view, name='user-list'),
    path('users/<int:pk>/edit/', views.user_update_view, name='user-update'),
    path('users/<int:pk>/password/', views.user_password_reset_view, name='user-password-reset'),
]
