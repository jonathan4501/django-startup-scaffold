from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import connection
from .views import HealthCheckView
from .response import BaseAPIViewResponse

User = get_user_model()

class HealthCheckTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.health_check_url = reverse('health-check')

    def test_health_check_success(self):
        """Test health check endpoint when all systems are operational"""
        response = self.client.get(self.health_check_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'Healthy')

    def test_health_check_db_failure(self):
        """Test health check endpoint when database is not accessible"""
        # Simulate DB connection failure by closing the connection
        connection.close()
        response = self.client.get(self.health_check_url)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data['status'], 'error')

class BaseAPIViewResponseTests(TestCase):
    def test_success_response(self):
        """Test successful API response format"""
        response = BaseAPIViewResponse(
            data={'key': 'value'},
            status=status.HTTP_200_OK,
            message='Success'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], {'key': 'value'})
        self.assertEqual(response.data['message'], 'Success')
        self.assertIsNone(response.data.get('errors'))

    def test_error_response(self):
        """Test error API response format"""
        response = BaseAPIViewResponse(
            status=status.HTTP_400_BAD_REQUEST,
            message='Validation error',
            errors={'field': ['Invalid value']}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Validation error')
        self.assertEqual(response.data['errors'], {'field': ['Invalid value']})
        self.assertIsNone(response.data.get('data'))

    def test_response_with_all_fields(self):
        """Test API response with all possible fields"""
        response = BaseAPIViewResponse(
            data={'key': 'value'},
            status=status.HTTP_201_CREATED,
            message='Created successfully',
            errors={'warning': ['Resource already exists']},
            extra_field='additional info'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data'], {'key': 'value'})
        self.assertEqual(response.data['message'], 'Created successfully')
        self.assertEqual(response.data['errors'], {'warning': ['Resource already exists']})
        self.assertEqual(response.data['extra_field'], 'additional info')

class CorePermissionsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='UserPass123!'
        )

    def test_admin_or_readonly_permission(self):
        """Test IsAdminOrReadOnly permission"""
        # Test GET request (should work for all users)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.health_check_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test POST request with regular user (should fail)
        response = self.client.post(self.health_check_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test POST request with admin user (should succeed)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.health_check_url, {})
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CoreMiddlewareTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_request_logging(self):
        """Test request logging middleware"""
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: Would need to check logs to verify logging occurred

    def test_error_handling(self):
        """Test error handling middleware"""
        # Test 404 handling
        response = self.client.get('/api/nonexistent/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('message', response.data)

        # Test 500 handling (would need to trigger a server error)
        # This is typically tested in integration tests

class CoreUtilsTests(TestCase):
    def test_core_utilities(self):
        """Test core utility functions"""
        # Add tests for utility functions in core/utils.py
        # This would depend on what utilities are implemented
        pass

class CoreValidatorsTests(TestCase):
    def test_core_validators(self):
        """Test core validators"""
        # Add tests for validators in core/validators.py
        # This would depend on what validators are implemented
        pass
