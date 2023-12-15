import datetime
import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Case, When, Q, F, Value
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from user.authenticate_utils import generate_otp

User = get_user_model()


def validate_mobile_phone(number: str):
    """Validates number start with '+98' or '0', then 10 digits"""
    number_pattern = re.compile(r'^(?:\+98|0)\d{10}$')
    result = number_pattern.match(number)
    if result:
        if number.startswith('0'):
            return '+98' + number[1:]
        return number
    else:
        raise ValidationError({'mobile_phone': 'Incorrect phone number format, must start with 0 or +98'})


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
        _("site"),
        to=Site,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="sites",
        default=settings.SITE_ID,
    )

    email = models.EmailField(
        _("email"),
        unique=True, null=False, blank=False, )
    mobile_phone = models.CharField(
        _("mobile phone"),
        unique=True, null=False, blank=False, max_length=19,
        validators=(validate_mobile_phone,)
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
        validators=[AbstractUser.username_validator],
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
    REQUIRED_FIELDS = []

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

    STATUS_READY = 0
    STATUS_USED = 1
    STATUS_UNUSABLE = 2
    STATUS_CHOICES = (
        (STATUS_READY, 'Ready'),
        (STATUS_USED, 'Used'),
        (STATUS_UNUSABLE, 'Unusable'),
    )

    user = models.OneToOneField(
        _("user"),
        to=User,
        on_delete=models.DO_NOTHING,
        null=False,
        blank=False,
        related_name="user",
    )

    # TODO what method to use for sending the token
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True, null=False, blank=False, editable=False)
    otp_token = models.fields.CharField(
        _("otp token"),
        max_length=19, null=False, blank=False, editable=False, default='hell-no',
    )
    status = models.fields.PositiveSmallIntegerField(
        _('status'),
        null=False, blank=False, default=STATUS_UNUSABLE, choices=STATUS_CHOICES,
    )

    class Meta:
        ordering = ["-created_at", "author"]

    @classmethod
    def check_otp_token_and_authenticate_db(
            cls,
            user_pk: int,
            otp_token: str,
    ) -> bool:

        """
        one time token and guarantee no race condition no d lock  trying to log in, use token more than once
        @param otp_token:
        @param user_pk:

        @return: true on validating otp token
        """

        with transaction.atomic():
            have_updated = OTPToken.objects.update(
                status=Case(
                    When(

                        Q(user_pk=user_pk)
                        &
                        Q(is_active=True)
                        &
                        Q(otp_token=otp_token)
                        &
                        Q(
                            (F('created_at') + timedelta(seconds=90)) < Now()
                        )
                        &
                        Q(status=OTPToken.STATUS_READY)
                        ,

                        then=Value(value=OTPToken.STATUS_USED, output_field=models.PositiveSmallIntegerField, ),
                    ),

                    default=Value(value=F('status'), output_field=models.PositiveSmallIntegerField, )
                    ,

                )
            ).select_for_update()

            if have_updated == 1:
                return True
            elif have_updated == 0:
                return False
            elif have_updated > 1:
                raise ValidationError("warning: multiple OTP authentication is going on!")

            return False

    @classmethod
    def generate_otp_token_db(cls, user_pk: int, mobile_phone: str, ) -> None:
        """
        one time token and guarantee no race condition no deadlock trying to log in, use token more than once
        @param mobile_phone:
        @param user_pk:

        @return: otp token
        """

        # generate otp token every 100 seconds per user id
        seconds_since_user_last_token = OTPToken.objects.filter(
            Q(user_pk=user_pk)
            &
            Q(is_active=True)
            &
            Q(
                (F('created_at') + timedelta(seconds=100)) < Now()
            )
        ).order_by('-created_at')[0:1].annotate(
            time_passed_token=Now() - F('created_at')
        )

        if len(seconds_since_user_last_token) > 0:
            seconds_since_user_last_token = seconds_since_user_last_token[0].time_passed_token
            if seconds_since_user_last_token < 100:
                return

        # if it has not been 100 seconds since the last token that been generated for the user just return the value
        # remaining = datetime.datetime.now() - (last_user_token['created_at'] + timedelta(100))

        # if remaining < timedelta(0):
        #     return remaining

        with transaction.atomic():
            OTPToken.objects.create(
                user_pk=user_pk,
                mobile_phone=mobile_phone,
                otp_token=generate_otp(),
            )
