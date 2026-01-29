from django.apps import AppConfig


class ApageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apage'

    def ready(self):
        import apage.signals  # Ensure signals are imported to connect them
