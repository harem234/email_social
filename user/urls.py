from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_view
from django.views.generic import TemplateView

from .views import PostLogoutView, CustomPasswordChangeView

urlpatterns = [
    path('login/',
         auth_view.LoginView.as_view(template_name='registration/login.html', success_url=reverse_lazy('login')),
         name='login'),
    path('logout/', PostLogoutView.as_view(), name='logout'),
    path('logged_out/',
         TemplateView.as_view(template_name='registration/logged_out.html'), name='logout_post'),

    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_view.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', auth_view.PasswordResetView.as_view(template_name='registration/password_reset_form.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_view.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_view.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_view.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
