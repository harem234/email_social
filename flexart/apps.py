from django.apps import AppConfig


class FlexartConfig(AppConfig):
    name = 'flexart'

    def ready(self):
        """
        Override this method in subclasses to run code when Django starts.
        """
        # for receiver decorator
        # from . import signals