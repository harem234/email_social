from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site


# hasattr(settings, 'SITE_ID')


# signal: pre_delete is set for SocialProvider
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
        db_column='social_provider',
    )

    client_id = models.CharField(blank=False, null=False, max_length=1000)

    def __str__(self):
        return self.social

    class Meta:
        verbose_name = 'Social_Provider'
        verbose_name_plural = 'Social_Providers'
        constraints = [
            models.UniqueConstraint(fields=['social', 'client_id'],
                                    name='every client_id  per social is unique'),
        ]


def get_sentinel_socialprovider():
    # return tuple
    return SocialProvider.objects.get_or_create(social='sentinel')[0]


# hasattr(settings, 'SITE_ID') and settings.SITE_ID


class SocialAccount(models.Model):
    from django.core.validators import EmailValidator

    site = models.ForeignKey(to=Site, on_delete=models.CASCADE, null=False, blank=False,
                             related_name="socialaccount_site", default=Site.objects.get_current().pk)

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False,
                             related_name="socialaccount_user")

    # signal: pre_delete is set for SocialAccount
    # on_delete: do Not delete social accounts on deleting a provider
    provider = models.ForeignKey(to=SocialProvider, on_delete=models.SET(get_sentinel_socialprovider), blank=False,
                                 null=False)

    social_id = models.CharField(blank=False, null=False, max_length=1000, )
    isConnected = models.BooleanField(null=False, blank=False, default=False, )

    email = models.CharField(blank=False, null=True, max_length=1000, unique=True, validators=[EmailValidator, ])

    credentials = models.TextField(blank=False, null=True, max_length=1000, )
    scopes = models.TextField(blank=False, null=True, max_length=1000, )

    def __str__(self):
        return self.user.email + "::" + self.provider.social

    class Meta:
        verbose_name = 'Social_Account'
        verbose_name_plural = 'Social_Accounts'
        # ensures for a user there is only one account per provider and per site at most
        constraints = [
            models.UniqueConstraint(fields=['user', 'provider', 'site'],
                                    name='user have one account per provider and site'),
            models.UniqueConstraint(fields=['social_id', 'provider', 'site'],
                                    name='every social_id per provider is unique for every site'),
        ]
