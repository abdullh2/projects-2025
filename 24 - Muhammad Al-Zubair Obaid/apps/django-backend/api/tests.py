# api/tests.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_ai_request_unauthenticated():
    """
    Tests that unauthenticated users receive a 401 Unauthorized response.
    """
    client = APIClient()
    url = reverse('ai-request')
    response = client.post(url, {"query": "test", "channel_name": "test_channel"})
    assert response.status_code == 401


@pytest.mark.django_db
@patch('api.views.ai_classifier', new_callable=AsyncMock)
@patch('api.views.grpc_client', new_callable=MagicMock)
def test_ai_request_authenticated(mock_grpc_client, mock_ai_classifier):
    """
    Tests a successful, authenticated request to the main AI endpoint.
    """
    # Setup Mocks
    mock_ai_classifier.classify.return_value = {
        "intent": "hardware_info",
        "entities": {}
    }
    mock_grpc_client.query_system_info = AsyncMock(return_value={"cpu_name": "Test CPU"})

    # Setup Test Client and User
    client = APIClient()
    user = User.objects.create_user(username='testuser', password='password')
    client.force_authenticate(user=user)

    # Make API Call
    url = reverse('ai-request')
    response = client.post(url, {"query": "specs", "channel_name": "test_channel"}, format='json')

    # Assertions
    assert response.status_code == 200
    assert response.data['intent'] == 'hardware_info'
    assert "Test CPU" in response.data['initial_response']
    mock_ai_classifier.classify.assert_called_once_with("specs")
    mock_grpc_client.query_system_info.assert_called_once()
