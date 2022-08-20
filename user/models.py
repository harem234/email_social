from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from django.db import models


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
        null=False,
        blank=False,
        related_name="user_site",
        default=settings.SITE_ID,
    )

    email = models.EmailField(unique=True, null=False, blank=False, )

    username = models.CharField(
        unique=True,
        blank=True,
        null=True,
        max_length=50,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
    )

    is_email_verified = models.BooleanField(blank=False, null=False, default=False)

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email.lower()
