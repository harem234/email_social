from typing import Any

from django.contrib.auth import views, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, RedirectURLMixin, \
    PasswordResetView, LogoutView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, FormView, TemplateView
from django.conf import settings
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN
from django.contrib.auth.decorators import login_not_required, login_required

from .forms import CustomUserCreationForm, OTPSMSRequestForm, OTPAuthenticationForm, EmailVerifyRequestForm, \
    CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm

User = get_user_model()

class CustomLoginView(LoginView):
    """
        Display the login form and handle the login action via email as username
    """
    form_class = CustomAuthenticationForm
    authentication_form = None
    template_name = "user/login.html"
    redirect_authenticated_user = True

    next_page = reverse_lazy('index')

class CustomLogoutView(LogoutView):
    """
    Log out the user and display the 'You are logged out' message.

    only with Post request user can log out, this adds more security.
    """
    http_method_names = ["post", "options"]
    template_name = "user/logged_out.html"
    next_page = reverse_lazy('logged_out')

class CustomRegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')
    template_name = 'user/register.html'


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'user/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'user/password_change_done.html'


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "user/password_reset_done.html"
    title = _("Password reset sent")

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "user/password_reset_confirm.html"
    title = _("Enter new password")

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "user/password_reset_complete.html"
    title = _("Password reset complete")

# verify email view: using django.contrib.auth.views.PasswordResetView as template
class EmailVerifyView(PasswordResetView):
    email_template_name = "user/verify_email.html"
    extra_email_context = None
    form_class = EmailVerifyRequestForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "user/verify_email_subject.txt"
    success_url = reverse_lazy("email_verify_sent")
    template_name = "user/verify_email_form.html"
    title = _("Verify Email")
    token_generator = default_token_generator


class EmailVerifySentView(PasswordResetDoneView):
    template_name = "user/verify_email_done.html" # todo
    title = _("Verification email sent")

default_token_generator = PasswordResetTokenGenerator()

@method_decorator(login_not_required, name="dispatch")
class EmailConfirmView(TemplateView):

    reset_url_token = "verify-email"
    success_url = reverse_lazy("email-verify-complete")
    template_name = "user/email_confirm.html"
    title = _("Verify Email")
    token_generator = default_token_generator

    def __init__(self, **kwargs: Any):
        super().__init__()
        self.validlink = None
        self.user = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            token = kwargs["token"]
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display confirmed email page.
                    self.validlink = True
                    self.user.is_email_verified = True
                    self.user.save()
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, self.reset_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "email confirm link is not valid" page.
        return self.render_to_response(self.get_context_data())

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            pk = User._meta.pk.to_python(uid)
            user = User._default_manager.get(pk=pk)
        except (
                TypeError,
                ValueError,
                OverflowError,
                User.DoesNotExist,
                ValidationError,
        ):
            user = None
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {
                    "title": _("Verify Email unsuccessful"),
                    "validlink": False,
                }
            )
        return context

# OTP authentication views


class TOTPLoginView(RedirectURLMixin, FormView):

    form_class = OTPSMSRequestForm
    authentication_form = None
    template_name = "user/OTP_request.html"  # todo OTP_request.html
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
    template_name = "user/OTP_login.html"  # todo OTP_login.html
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
