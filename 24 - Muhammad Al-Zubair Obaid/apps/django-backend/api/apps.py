# api/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """
        This method is called when the Django app is ready.
        It's the correct place to initialize singletons or background services.
        """
        logger.info("Initializing application services (AI Classifier)...")
        # This import triggers the singleton instantiation in services.py
        from . import services
        services.initialize_services()
