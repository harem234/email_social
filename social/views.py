from django.contrib.sites.models import Site
from django.db import transaction
from django.contrib.auth import get_user_model
from social.models import SocialAccount

USER_MODEL = get_user_model()

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
def create_social_create_email_user(social_id, email, provider_id, is_email_verified=False, ):
    """
    if user exists just add the social
    if user does not exists, create user and add social

    """
    emailUser, isCreated = USER_MODEL.objects.get_or_create(
        email=email,
        defaults={'site': Site.objects.get_current(),
                  'isEmailVerified': is_email_verified}, )

    # if not isCreated:
    #     # raise and the transaction rollback
    #     raise ValueError("EmailUser already exist PK: %d" % emailUser.pk)

    socialAccount, isCreated = SocialAccount.objects.get_or_create(
        site=Site.objects.get_current(),
        user=emailUser,
        provider_id=provider_id,
        defaults={
            'social_id': social_id,
            'is_connected': True,
            'email': email, })

    # if not isCreated:
    #     # raise and the transaction rollback
    #     raise ValueError("SocialAccount already exist PK: %d" % socialAccount.pk)

    return (emailUser, socialAccount,)


@transaction.atomic
def create_social_for_user(user, social_id, provider_id, site=None, **kwargs):
    return SocialAccount.objects.create(
        site=site or Site.objects.get_current(),
        user=user, provider_id=provider_id,
        social_id=social_id,
        is_connected=True,
        email=kwargs.get('email'),
        kwargs=kwargs
        )
