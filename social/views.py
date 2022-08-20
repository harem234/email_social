from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db import transaction

from social.models import SocialAccount, SocialProvider

"""
    create social account
    create emailuser account
    relate emailuser and social accounts
    set isEmailVerified for emailuser
    
    raise: ValueError
        if emailuser and/or social account already exist
    transaction: both (email user and social account)must be made together or nothing 
"""


@transaction.atomic
def create_social_create_email_user(social_id, email, provider, is_email_verified=False, ):
    emailUser, isCreated = get_user_model().objects.get_or_create(email=email,
                                                                  defaults={'site': Site.objects.get_current(),
                                                                            'isEmailVerified': is_email_verified}, )

    if not isCreated:
        # raise and the transaction rollback
        raise ValueError("EmailUser already exist PK: %d" % emailUser.pk)

    socialAccount, isCreated = SocialAccount.objects.get_or_create(site=Site.objects.get_current(),
                                                                   user=get_user_model().objects.get(email=email),
                                                                   provider=provider,
                                                                   defaults={
                                                                       'social_id': social_id, 'isConnected': True,
                                                                       'email': email, })

    if not isCreated:
        # raise and the transaction rollback
        raise ValueError("SocialAccount already exist PK: %d" % socialAccount.pk)


@transaction.atomic
def create_social_for_user(user, social_id, **kwargs):
    SocialAccount.objects.create(site=Site.objects.get_current(), user=user, provider=SocialProvider.objects.get(
        social='google'), social_id=social_id, isConnected=True, email=kwargs.get('email'), )
