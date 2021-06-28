from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.validators import EmailValidator

if hasattr(settings, 'SITE_ID'):
    SITE_ID = settings.SITE_ID
else:
    raise ValueError('SITE_ID is required in settings.')

def get_sentinel_socialprovider():
    return SocialProvider.objects.get_or_create(social='sentinel')[0]

class SocialProvider(models.Model):
    SENTINEL = 'sentinel'
    GOOGLE = 'google'
    GITHUB = 'github'
    Social_List = [
        (None, 'Select Provider'),
        (GOOGLE, 'Google'),
        (GITHUB, 'Github'),

        # for deleted provider of SocialAccount instances
        (SENTINEL, 'sentinel'),
    ]
    social = models.CharField(
        unique=True,
        max_length=10,
        choices=Social_List,
        null=False,
        blank=False,
    )

    client_id = models.CharField(blank=False, null=False, max_length=300)
    credential = models.TextField(blank=False, null=False, max_length=1500)

    def __str__(self):
        return self.social

    class Meta:
        verbose_name = 'Social Provider'
        verbose_name_plural = 'Social Providers'
        constraints = [
            models.UniqueConstraint(fields=('social', 'client_id',),
                                    name='every client_id  per social is unique'),
            
            models.UniqueConstraint(fields=('social', 'client_id',),
                                    name='every credential  per social is unique'),
        ]


class SocialAccount(models.Model):
    """
    signal: pre_delete is set for SocialProvider
    """
    site = models.ForeignKey(to=Site, on_delete=models.DO_NOTHING, 
        null=False, blank=False,
        related_name="socialaccount_site", default=SITE_ID)

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False,
                             related_name="socialaccount_user")

    # signal: pre_delete is set for SocialAccount
    # on_delete: do Not delete social accounts on deleting a provider
    provider = models.OneToOneField(
        to=SocialProvider,
        on_delete=models.SET(get_sentinel_socialprovider),
        blank=False,
        null=False,
        )

    social_id = models.CharField(blank=False, null=False, max_length=1000, )
    is_connected = models.BooleanField(null=False, blank=False, default=False, )

    email = models.CharField(
        blank=False, null=True, max_length=300, unique=True, validators=(EmailValidator,))

    credentials = models.TextField(blank=True, null=True, max_length=1000, )
    scopes = models.TextField(blank=True, null=True, max_length=1000, )

    def __str__(self):
        return self.user.email + "::" + self.provider.social

    class Meta:
        verbose_name = 'Social Account'
        verbose_name_plural = 'Social Accounts'
        # ensures for a user there is only one account per provider and per site at most
        constraints = (
            models.UniqueConstraint(fields=('user', 'provider', 'site'),
                                    name='user have one account per provider and site'),

            models.UniqueConstraint(fields=('social_id', 'provider', 'site'),
                                    name='every social_id per provider is unique for every site'),
        )
