# website/apps.py
from django.apps import AppConfig

class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def ready(self):
        import website.signals

from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'website'

    def ready(self):
        import website.signals  # Make sure to import the signals module