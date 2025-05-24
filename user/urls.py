# from django.contrib.auth import views as auth_view
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from .views import CustomLogoutView, CustomPasswordChangeView, EmailVerifyView, CustomLoginView, \
    CustomPasswordChangeDoneView, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, \
    CustomPasswordResetCompleteView

urlpatterns = [
    path('login/',
         CustomLoginView.as_view(
             template_name='registration/login.html',
         ),
         name='login'
    ),

    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('logged_out/',
         TemplateView.as_view(
             template_name='registration/logged_out.html'
         ),
         name='logout_post'),


    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),

    path('password_change/done/',
         CustomPasswordChangeDoneView.as_view(),
         name='password_change_done'
    ),


    path('password_reset/', CustomPasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
        ),
         name='password_reset'
    ),

    path('password_reset/done/',
         CustomPasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         CustomPasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),


    # request verify email
    path(
        'email/email-confirm-request/',
        EmailVerifyView.as_view(),
        name='email_verify',
    ),

    path(
        'email/request-verify-email/',
        EmailVerifyView.as_view(),
        name='email_request_verify'),

    path(
        'email/verify-email/<uidb64>/<token>/',
        EmailVerifyView.as_view(),
        name='email_verification_link'),
]
