from django.apps import AppConfig


class TransactionApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transaction_api'

    #def ready(self):
    #    from transaction_api import signals
