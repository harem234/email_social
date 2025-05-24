from django.contrib.auth import views, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, RedirectURLMixin, \
    PasswordResetView, LogoutView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, FormView, TemplateView
from django.conf import settings
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN

from .forms import CustomUserCreationForm, OTPSMSRequestForm, OTPAuthenticationForm, EmailVerifyRequestForm, \
    CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm

User = get_user_model()

class CustomLoginView(LoginView):
    """
        Display the login form and handle the login action via email as username
    """
    form_class = CustomAuthenticationForm
    authentication_form = None
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    next_page = reverse_lazy('FLEX:index')
    # extra_context = {'next': reverse_lazy('FLEX:index')}

class CustomLogoutView(LogoutView):
    """
    Log out the user and display the 'You are logged out' message.

    only with Post request user can log out, this adds more security.
    """
    http_method_names = ["post", "options"]
    template_name = "registration/logged_out.html"
    next_page = reverse_lazy('logged_out')

class CustomSignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    # model object
    # context_object_name = 'signup_model'

    # form instance name in context
    # context_form_name = 'signup_form'

class EmailPhoneLoginView(LoginView):
    template_name = 'registration/password_change_form.html'
    extra_context = {'next': reverse_lazy('index')}


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"
    title = _("Password reset sent")

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "registration/password_reset_confirm.html"
    title = _("Enter new password")

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
    title = _("Password reset complete")

# verify email view: using django.contrib.auth.views.PasswordResetView as template
class EmailVerifyView(PasswordResetView):
    email_template_name = "registration/verify_email.html"
    extra_email_context = None
    form_class = EmailVerifyRequestForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "registration/verify_email_subject.txt"
    success_url = reverse_lazy("verify_email_done")
    template_name = "registration/verify_email_form.html"
    title = _("Verify Email")
    token_generator = default_token_generator


default_token_generator = PasswordResetTokenGenerator()

class EmailConfirmView(TemplateView):

    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):

        self.user = self.get_user(kwargs["uidb64"])
        session_token = request.session.get(INTERNAL_RESET_SESSION_TOKEN)

        if self.token_generator.check_token(self.user, session_token):
            self.user.is_email_verified = True
            self.user.save()

        else:

            super().get(request, *args, **kwargs)

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.user = None


# OTP authentication views


class OTPRequestView(RedirectURLMixin, FormView):

    form_class = OTPSMSRequestForm
    authentication_form = None
    template_name = "registration/OTP_request.html" # todo OTP_request.html
    redirect_authenticated_user = False
    extra_context = None

    def get_default_redirect_url(self):
        """
        Return the default redirect URL.
        """
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url(settings.OTP_REQUEST_REDIRECT_URL) # todo OTP_REQUEST_REDIRECT_URL

class OTPLoginView(LoginView):

    form_class = OTPAuthenticationForm
    authentication_form = None
    template_name = "registration/OTP_login.html" # todo OTP_login.html
    redirect_authenticated_user = False
    extra_context = None

    def get_default_redirect_url(self):
        """
        Return the default redirect URL.
        """
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url(settings.OTP_LOGIN_REDIRECT_URL) # todo OTP_LOGIN_REDIRECT_URL
