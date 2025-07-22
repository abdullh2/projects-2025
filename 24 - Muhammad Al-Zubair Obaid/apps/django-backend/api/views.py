# api/views.py
import logging
from asgiref.sync import async_to_sync 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .services import ai_classifier_instance as ai_classifier
from .services import response_formatter_instance as response_formatter

logger = logging.getLogger(__name__)

class AiRequestView(APIView):
    permission_classes = [AllowAny]

    # The public method is now synchronous
    def post(self, request, *args, **kwargs):
        return async_to_sync(self.handle_async_post)(request, *args, **kwargs)

    async def handle_async_post(self, request, *args, **kwargs):
        """The actual asynchronous logic of the view."""
        query = request.data.get("query")
        if not query:
            return Response({"error": "Query is required."}, status=status.HTTP_400_BAD_REQUEST)

        # The view's only job now is to classify and return the result.
        # The frontend will decide if a gRPC call is needed.
        classification_result = await ai_classifier.classify(query)
        initial_response = response_formatter.generate_response(classification_result)
        
        response_data = {
            "initial_response": initial_response,
            "intent": classification_result.get("intent"),
            "entities": classification_result.get("entities", {})
        }
        return Response(response_data, status=status.HTTP_200_OK)
