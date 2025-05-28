from django.urls import path, reverse_lazy, resolve
from django.views.generic import TemplateView

from user.views import CustomLoginView, CustomPasswordChangeView, CustomPasswordChangeDoneView, \
    CustomLogoutView, CustomRegisterView

app_name = 'FLEX'

urlpatterns = [
    # template_name :: match the path of template relative to template directory
    path('about/', TemplateView.as_view(template_name="flexart/about.html"),
         name="about"),
    path('contact/', TemplateView.as_view(template_name="flexart/contact.html"),
         name="contact"),
    path('errorpage/', TemplateView.as_view(template_name="flexart/errorpage.html"),
         name="errorpage"),
    path('features/', TemplateView.as_view(template_name="flexart/features.html"),
         name="features"),
    path('pricing/', TemplateView.as_view(template_name="flexart/pricing.html"),
         name="pricing"),
    path('pricing_light/', TemplateView.as_view(template_name="flexart/pricing_light.html"),
         name="pricing_light"),
    path('projects/', TemplateView.as_view(template_name="flexart/projects.html"),
         name="projects"),
    path('team/', TemplateView.as_view(template_name="flexart/team.html"),
         name="team"),

    path('index/', TemplateView.as_view(template_name='flexart/index.html'), name="index"),

    # auth urls login logout signup


    path('logout/', CustomLogoutView.as_view(
        next_page=reverse_lazy('FLEX:index'),
        template_name='flexart/index.html'
        ),
        name="logout"
    ),

    # path('logged_out/',
    #      TemplateView.as_view(template_name='flexart/index.html'), name='logged_out'),


    path('login/', CustomLoginView.as_view(
            template_name='flexart/index_login.html',
        ),
        name="login"
    ),

    path(
    'register/',
         CustomRegisterView.as_view(
             success_url=reverse_lazy('FLEX:login'),
             template_name='flexart/index_register.html'
         ),
         name="signup"
    ),

    # password change
    path('password_change/',
         CustomPasswordChangeView.as_view(
             template_name='flexart/index_password_change_form.html',
             success_url=reverse_lazy('FLEX:password_change_done')),
         name="password_change"),

    path('password_change/done/',
         CustomPasswordChangeDoneView.as_view(template_name='flexart/index_password_change_done.html'),
         name="password_change_done"),

    # password reset
    # get email
    # path('password_reset/',
    #      CustomPasswordResetView.as_view(template_name='flexart/password_reset_form.html',
    #                                email_template_name='flexart/password_reset_email.html',
    #                                success_url=reverse_lazy('FLEX:password_reset_done')),
    #      name='password_reset'),
    # # email found and send
    # path('password_reset/done/',
    #      PasswordResetDoneView.as_view(template_name='flexart/password_reset_done.html'),
    #      name='password_reset_done'),
    #
    # # get the email and come to reset password page
    # path('reset/<uidb64>/<token>/',
    #      PasswordResetConfirmView.as_view(template_name='flexart/password_reset_confirm.html',
    #                                       success_url=reverse_lazy('FLEX:password_reset_complete')),
    #      name='password_reset_confirm'),
    #
    # path('reset/done/',
    #      PasswordResetCompleteView.as_view(template_name='flexart/password_reset_complete.html'),
    #      name='password_reset_complete'),
]