from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import SocialProvider

# when a provider is deleting all account's with that provider will have isConnected=False
@receiver(pre_delete, sender=SocialProvider, dispatch_uid="socialprovider_A1", )
def my_handler1(sender, **kwargs):
    social = kwargs['instance'].social
    SocialProvider.objects.get(social=social).socialaccount_set.all().update(isConnected=False)
