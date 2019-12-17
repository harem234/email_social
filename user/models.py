from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site

"""related_name protocol for foreignKey
<from table name>_<to table name> """


class EmailUser(AbstractUser):
    site = models.ForeignKey(to=Site, on_delete=models.CASCADE, null=False, blank=False, related_name="user_site",
                             default=Site.objects.get_current().pk, db_column='site')
    # new USERNAME_FIELD (email) must be overwrite and be required so: manage.py createsuperuser runs
    email = models.EmailField(unique=True, null=False, blank=False, )
    username = models.CharField(
        blank=True, null=True, max_length=50,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
    )
    isEmailVerified = models.BooleanField(blank=False, null=False, default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email.lower()
