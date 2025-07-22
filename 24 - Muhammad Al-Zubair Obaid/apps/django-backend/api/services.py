# api/services.py
import logging
from .intent_classifier.classifier import MultilingualIntentClassifier, ResponseFormatter

logger = logging.getLogger(__name__)

# These will hold the singleton instances. They are initialized as None.
ai_classifier_instance = None
response_formatter_instance = None


def initialize_services():
    """
    Initializes the singleton services. This function is called once from AppConfig.ready().
    """
    global ai_classifier_instance, response_formatter_instance

    if ai_classifier_instance is None:
        logger.info("Loading MultilingualIntentClassifier singleton...")
        # The path needs to be correct from the project root where manage.py is run.
        ai_classifier_instance = MultilingualIntentClassifier()
        logger.info("AI Classifier loaded.")

    if response_formatter_instance is None:
        logger.info("Loading ResponseFormatter singleton...")
        response_formatter_instance = ResponseFormatter()
        logger.info("Response Formatter loaded.")

