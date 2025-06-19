from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import AIQuery

User = get_user_model()

class AIQueryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.client.login(email='testuser@example.com', password='testpass')
        self.url = reverse('aiquery-list')  # Assuming router registered with basename 'aiquery'

    @patch('ai_assistant.views.openai.ChatCompletion.create')
    def test_create_query_response(self, mock_openai_create):
        mock_openai_create.return_value = {
            'choices': [{'message': {'content': 'This is a mocked AI response.'}}]
        }
        data = {
            'query_text': 'Hello AI',
            'use_case': 'test_case',
            'language': 'en'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['response_text'], 'This is a mocked AI response.')
        self.assertEqual(response.data['use_case'], 'test_case')
        self.assertEqual(AIQuery.objects.count(), 1)
        ai_query = AIQuery.objects.first()
        self.assertEqual(ai_query.user, self.user)

    def test_permissions(self):
        self.client.logout()
        data = {'query_text': 'Test'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_sees_only_their_queries(self):
        other_user = User.objects.create_user(email='other@example.com', password='testpass')
        AIQuery.objects.create(user=other_user, query_text='Other user query')
        AIQuery.objects.create(user=self.user, query_text='My query')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data:
            self.assertEqual(item['user'], self.user.id)
