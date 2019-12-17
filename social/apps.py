from django.apps import AppConfig


class SocialConfig(AppConfig):
    name = 'social'

    def ready(self):
        """
        Override this method in subclasses to run code when Django starts.
        """
        # for receiver decorator
        from . import signals
