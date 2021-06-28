from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from django.conf import settings
from django.urls.base import reverse
from django.utils.translation import gettext_lazy as _

"""related_name protocol for foreignKey
<from table name>_<to table name> """


class EmailUser(AbstractUser):

    username_validator = UnicodeUsernameValidator()
    # default=Site.objects.get_current()
    site = models.ForeignKey(to=Site, on_delete=models.CASCADE, null=False, blank=False, related_name="user_site",
                             default=settings.SITE_ID)
    # new USERNAME_FIELD (email) must be overwrite and be required so: manage.py createsuperuser runs
    email = models.EmailField(unique=True, null=False, blank=False, )
    username = models.CharField(
        _('username'),
        blank=True, null=True, max_length=150,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=(username_validator, ),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    isEmailVerified = models.BooleanField(
        blank=False, null=False, default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    def __str__(self):
        return self.email.lower()

    def get_absolute_url(self):
        return reverse('user_detail', args=(str(self.id), ))
