import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models, transaction, DatabaseError
from django.db.models import Case, When, Q, F, Value, PositiveSmallIntegerField
from django.db.models.functions import Now
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from user.authenticate_utils import generate_otp


# def validate_mobile_phone(number: str):
#     """Validates number start with '+98' or '0', then 10 digits"""
#     number_pattern = re.compile(r'^(?:\+98|0)\d{10}$')
#     result = number_pattern.match(number)
#     if result:
#         if number.startswith('0'):
#             return '+98' + number[1:]
#         return number
#     else:
#         raise ValidationError({'mobile_phone': 'Incorrect phone number format, must start with 0 or +98'})

phone_regex = RegexValidator(
        regex=r'^\+?\d{8,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

class EmailUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)

        if 'username' in extra_fields:
            extra_fields['username'] = self.model.normalize_username(extra_fields['username'])

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class EmailUser(AbstractUser):

    site = models.ForeignKey(
        to=Site,
        on_delete=models.CASCADE,
        related_name="sites",
        null=False,
        blank=False,
        default=settings.SITE_ID,
    )

    email = models.EmailField(
        _("email"),
        unique=True, null=False, blank=False,
    )

    mobile_phone = models.CharField(
        _("mobile phone"),
        unique=True, null=True, blank=True, max_length=19,
        validators=(phone_regex,),
        help_text=_(
            "at most 19 characters of digits only"
        ),
    )

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=(AbstractUser.username_validator,),
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    is_email_verified = models.BooleanField(
        _("is email verified"),
        blank=False,
        null=False,
        default=False,

    )
    is_mobile_phone_verified = models.BooleanField(
        _("is mobile phone verified"),

        null=False,
        default=False,

        blank=False,
        help_text='must verified with otp',

    )

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    MOBILE_FIELD = 'mobile_phone'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = [ ]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = False

    @classmethod
    def get_mobile_phone_field_name(cls) -> str:
        try:
            return cls.MOBILE_FIELD
        except AttributeError:
            return "email"

    def __str__(self):
        return self.email.lower() or self.mobile_phone.lower() or self.username.lower()


class OTPToken(models.Model):
    """
    ready : ready to sign user
    used : accessed once to sign in used once successful or unsuccessful
    unusable: otp token not usable expired

    add vacuum base on created_at field
    """
    STATUS_EMPTY = 0
    STATUS_GENERATED = 1
    STATUS_VERIFIED = 2
    STATUS_NOT_VERIFIED = 3
    STATUS_CHOICES = (
        (STATUS_GENERATED, 'Generated'),
        (STATUS_VERIFIED, 'Verified'),
        (STATUS_NOT_VERIFIED, 'Not Verified'),
        (STATUS_EMPTY, 'EMPTY'),
    )

    SEND_BY_SMS = 0
    SEND_BY_EMAIL = 1
    SEND_BY_CHOICES = (
        (SEND_BY_SMS, 'SMS'),
        (SEND_BY_EMAIL, 'Email'),
    )

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="tokens",
        related_query_name="tokens",
    )

    send_by = models.fields.PositiveSmallIntegerField(
        _('status'),
        null=False, blank=False, default=SEND_BY_EMAIL, choices=SEND_BY_CHOICES,
    )

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True, null=False, blank=False, editable=False,
    )

    expire_at = models.DateTimeField(
        _("expire at"),
        auto_now=True, null=False, blank=False, editable=False,
    )

    otp_token = models.fields.CharField(
        _("otp token"),
        max_length=19, null=False, blank=False, editable=False,
    )

    status = models.fields.PositiveSmallIntegerField(
        _('status'),
        null=False, blank=False, default=STATUS_EMPTY, choices=STATUS_CHOICES,
    )

    log_mobile_phone = models.CharField(
        _("log mobile phone"),
        null=False,
        blank=True,
        max_length=19,
        help_text=_(
            "at most 19 characters of digits only"
        ),
    )

    class Meta:
        ordering = [ "user_id", "-created_at", "-expire_at", ]

    # todo add to celery
    @classmethod
    def check_otp_token(cls, user_pk: int, otp_token: str, ) -> 'OTPToken':
        """
        one time token and guarantee no race condition no deadlock trying to log in, use token more than once
        @param otp_token:
        @param user_pk:

        @return: otp token object
        """

        with transaction.atomic():

            for i in range(3):

                # try to lock raw where user has otp
                try:
                    otp_qs = OTPToken.objects.filter(
                        user_pk=user_pk, otp_token=otp_token
                    ).select_for_update(nowait=True)[0:1]

                    otp = otp_qs[0]

                except DatabaseError:
                    print("user.models:OTPToken.check_otp_token ","at try:", i+1, "  -->  " , DatabaseError)

                else:

                    if (
                        otp.otp_token == otp_token
                        and
                        otp.expire_at < timezone.now()
                        and
                        otp.status == OTPToken.STATUS_GENERATED
                    ):

                        otp.status = OTPToken.STATUS_VERIFIED
                    else:
                        otp.status = OTPToken.STATUS_NOT_VERIFIED

                    otp.save()

                    # after successful access to user otp row in db do not try again
                    break

            return otp

    @classmethod
    def create_otp_token(cls, user_pk: int, send_by: int, ):
        """
        one time token and guarantee no race condition no deadlock trying to log in, use token more than once
        @param send_by:
        @param user_pk:

        @return: otp token object
        """

        with transaction.atomic():

            otp_qs = OTPToken.objects.filter(user_pk=user_pk).order_by('-created_at').select_for_update(nowait=True)[0:1]

            if len(otp_qs) == 1:

                otp = otp_qs[0:1].get()

                if otp.expire_at < timezone.now():
                    return otp

                # else otp is expired

            # so token is expired or there is no token generated for the user
            otp_token = generate_otp()
            return OTPToken.objects.create(
                user_pk=user_pk,
                otp_token=otp_token,
                send_by=send_by,
                status=OTPToken.STATUS_GENERATED
            )