import logging

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordResetForm, \
    PasswordChangeForm, _unicode_ci_compare, UsernameField
from django import forms
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.utils.text import capfirst


from .models import validate_mobile_phone, OTPToken
from .send_to_apis import send_otp_to_console

User = get_user_model()
logger = logging.getLogger("dj_project.user.forms")

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = '__all__'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class CustomPasswordChangeForm(PasswordChangeForm):
    pass

# this is copied from PasswordResetForm and changed
class EmailVerifyRequestForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        try:
            email_message.send()
        except Exception:
            logger.exception(
                "Failed to send password reset email to %s", context["user"].pk
            )

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = User.get_email_field_name()
        active_users = User._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/email_verify_request_subject.txt",
        email_template_name="registration/email_verify_request.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = User.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )

class MobileLinkPasswordResetForm(PasswordResetForm):
    """
    change password with OTP token authentication
    """

    email = None

    mobile_phone = forms.CharField(
        label=_("mobile phone"),
        strip=True,
        widget=forms.widgets.TextInput(attrs={"autocomplete": "tel", "autofocus": True}),
        validators=(validate_mobile_phone,)
    )

    def send_sms(
            self,
            context,
            from_mobile,
            to_mobile,
            sms_template_name='password_reset_sms.html',
    ):
        """
        Send a sms to `to_mobile`
        """
        body = loader.render_to_string(sms_template_name, context)

        # send_sms.send(from_mobile, to_mobile, body)
        send_otp_to_console
    def get_users(self, mobile):
        """Given a mobile, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
    #     mobile_phone_field_name = User.get_mobile_phone_field_name()
    #     active_users = User._default_manager.filter(
    #         **{
    #             "%s__iexact" % mobile_phone_field_name: mobile,
    #             "is_active": True,
    #         }
    #     )
    #     return (
    #         u
    #         for u in active_users
    #         if u.has_usable_password()
    #            and _unicode_ci_compare(mobile, getattr(u, mobile))
    #     )
    #
    # def save(
    #         self,
    #         token_generator=default_token_generator,
    #         sender_mobile_phone=None,
    #         request=None,
    #         use_https=False,
    #         domain_override=None,
    #         extra_sms_context=None,
    #         html_sms_template_name='password_reset_email.html',
    # ):
    #
    #     """
    #     Generate a one-use only link for resetting password and send it to the
    #     user.
    #     """
    #
    #     if not domain_override:
    #         current_site = get_current_site(request)
    #         site_name = current_site.name
    #         domain = current_site.domain
    #     else:
    #         site_name = domain = domain_override
    #
    #     mobile = self.cleaned_data["mobile"]
    #     mobile_phone_field_name = User.get_mobile_phone_field_name()
    #
    #     for user in self.get_users(mobile):
    #         user_mobile = getattr(user, mobile_phone_field_name)
    #         context = {
    #             "mobile": user_mobile,
    #             "domain": domain,
    #             "site_name": site_name,
    #             "uid": urlsafe_base64_encode(force_bytes(user.pk)),
    #             "user": user,
    #             "token": token_generator.make_token(user),
    #             "protocol": "https" if use_https else "http",
    #             **(extra_sms_context or {}),
    #         }
    #
    #         self.send_sms(
    #             context,
    #             from_mobile=sender_mobile_phone,
    #             to_mobile=user_mobile,
    #             sms_template_name=html_sms_template_name,
    #         )

class OTPSMSRequestForm(forms.Form):
    """
       request OTP token
        if there is a mobile with active user then there will be an SMS for it
    """

    mobile = forms.CharField(
        label=_("mobile"),
        widget=forms.TextInput(attrs={"autofocus": True}),
        validators=(validate_mobile_phone,)
    )

    error_messages = {
        "invalid_mobile": _(
            "Please enter a correct %(mobile)s"
        ),
        # "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "MOBILE_FIELD" field.
        self.mobile_field = User._meta.get_field(User.MOBILE_FIELD)
        mobile_max_length = self.mobile_field.max_length or 254
        self.fields["mobile"].max_length = mobile_max_length
        self.fields["mobile"].widget.attrs["mobile"] = mobile_max_length
        if self.fields["mobile"].label is None:
            self.fields["mobile"].label = capfirst(self.mobile_field.verbose_name)

    def save(self):
        mobile_field_name = User.get_mobile_field()
        user_obj = User._default_manager.get(
            **{
                "%s__iexact" % mobile_field_name: self.cleaned_data["mobile"],
                "is_active": True,
            }
        )

        if user_obj is True:
            token_obj = OTPToken.create_otp_token(user_obj.pk, OTPToken.SEND_BY_SMS)
            # send_otp(token_obj)

class OTPAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    mobile_phone = forms.CharField(

        label=_("mobile"),
        widget=forms.TextInput(attrs={"autofocus": True}),
        validators=(validate_mobile_phone,)
    )

    otp_token = forms.CharField(
        label=_("OTP token"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "received token"}),
    )

    error_messages = {
        "invalid_login": _(
            _("Please enter a correct OTP code with-in the time frame")
        ),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        self.mobile_field = User._meta.get_field(User.MOBILE_FIELD)
        mobile_max_length = self.mobile_field.max_length or 29

        self.fields["mobile_phone"].max_length = mobile_max_length
        self.fields["mobile_phone"].widget.attrs["mobile"] = mobile_max_length
        if self.fields["mobile_phone"].label is None:
            self.fields["mobile_phone"].label = capfirst(self.mobile_field.verbose_name)

    def clean(self):
        mobile_phone = self.cleaned_data.get("mobile_phone")
        otp_token = self.cleaned_data.get("otp_token")

        if (mobile_phone is not None ) and (otp_token is not None) :
            self.user_cache = authenticate(
                self.request, mobile_phone=mobile_phone, otp_token=otp_token
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

        return None

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"mobile_phone": self.mobile_field.verbose_name},
        )
