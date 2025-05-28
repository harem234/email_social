from django.urls import path
from django.views.generic import TemplateView
from .views import CustomLogoutView, CustomPasswordChangeView, CustomLoginView, \
    CustomPasswordChangeDoneView, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, \
    CustomPasswordResetCompleteView, CustomRegisterView, EmailVerifyView, EmailConfirmView, \
    EmailVerifySentView

urlpatterns = [

    path('login/',
         CustomLoginView.as_view(
             template_name='user/login.html',
         ),
         name='login'
    ),

    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('logged_out/',
         TemplateView.as_view(
             template_name='user/logged_out.html'
         ),
         name='logged_out'),

    path('index/',
             TemplateView.as_view(
                 template_name='user/index.html'
             ),
             name='index'),

    path('register/', CustomRegisterView.as_view(), name='register'),

    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),

    path('password_change/done/',
         CustomPasswordChangeDoneView.as_view(),
         name='password_change_done'
    ),


    path('password_reset/', CustomPasswordResetView.as_view(
        template_name='user/password_reset_form.html'
        ),
         name='password_reset'
    ),

    path('password_reset/done/',
         CustomPasswordResetDoneView.as_view(
             template_name='user/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(
             template_name='user/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         CustomPasswordResetCompleteView.as_view(
             template_name='user/password_reset_complete.html'
         ),
         name='password_reset_complete'),


    # email verification


    path(
        'email/email-verify-request/',
        EmailVerifyView.as_view(),
        name='email_verify_request',
    ),

    path(
        'email/email_verify_sent/',
        EmailVerifySentView.as_view(),
        name='email_verify_sent',),

    path(
        'email/verify-email-link/<uidb64>/<token>/',
        EmailConfirmView.as_view(),
        name='email_verification_link'),
]
