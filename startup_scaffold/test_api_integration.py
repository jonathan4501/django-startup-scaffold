"""
Comprehensive API Integration Tests
Tests all major API endpoints and functionality to ensure deployment readiness
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
import json

# Import models from all apps
from accounts.models import CustomUser
from jobs.models import Job, JobApplication
from services.models import Service, ServiceCategory
from messaging.models import Conversation, Message
from payments.models import Payment, PaymentMethod
from ratings.models import Rating
from notifications.models import Notification

User = get_user_model()

class APIIntegrationTests(APITestCase):
    """
    Comprehensive integration tests for all API endpoints
    """
    
    def setUp(self):
        """Set up test data for integration tests"""
        self.client = APIClient()
        
        # Create test users
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='TestPass123!',
            first_name='Client',
            last_name='User',
            role='CLIENT'
        )
        
        self.worker_user = User.objects.create_user(
            email='worker@example.com',
            password='TestPass123!',
            first_name='Worker',
            last_name='User',
            role='WORKER'
        )
        
        self.service_provider = User.objects.create_user(
            email='provider@example.com',
            password='TestPass123!',
            first_name='Service',
            last_name='Provider',
            role='SERVICE_PROVIDER'
        )
        
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User'
        )

    def test_authentication_flow(self):
        """Test complete authentication flow"""
        # Test registration
        register_data = {
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'password2': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'WORKER'
        }
        
        response = self.client.post(reverse('auth-register'), register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Test login
        login_data = {
            'email': 'newuser@example.com',
            'password': 'NewPass123!'
        }
        
        response = self.client.post(reverse('auth-login'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # Test current user endpoint
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get(reverse('auth-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newuser@example.com')

    def test_job_workflow(self):
        """Test complete job posting and application workflow"""
        self.client.force_authenticate(user=self.client_user)
        
        # Create a job
        job_data = {
            'title': 'Test Job Posting',
            'description': 'This is a test job description',
            'budget': '150.00',
            'max_workers': 2,
            'location': 'Test City',
            'requirements': ['Python', 'Django'],
            'status': 'OPEN'
        }
        
        response = self.client.post(reverse('job-list'), job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job_id = response.data['id']
        
        # Worker applies to job
        self.client.force_authenticate(user=self.worker_user)
        
        application_data = {
            'job': job_id,
            'cover_letter': 'I am interested in this job'
        }
        
        response = self.client.post(reverse('jobapplication-list'), application_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Client hires worker
        self.client.force_authenticate(user=self.client_user)
        
        hire_data = {'worker_id': str(self.worker_user.id)}
        response = self.client.post(reverse('job-hire', args=[job_id]), hire_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify job status changed
        response = self.client.get(reverse('job-detail', args=[job_id]))
        self.assertEqual(response.data['status'], 'IN_PROGRESS')

    def test_service_workflow(self):
        """Test service creation and booking workflow"""
        # Create service category (admin only)
        self.client.force_authenticate(user=self.admin_user)
        
        category_data = {
            'name': 'Home Services',
            'description': 'Various home services',
            'is_active': True
        }
        
        response = self.client.post(reverse('servicecategory-list'), category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category_id = response.data['id']
        
        # Service provider creates service
        self.client.force_authenticate(user=self.service_provider)
        
        service_data = {
            'category': category_id,
            'title': 'House Cleaning Service',
            'description': 'Professional house cleaning',
            'price': '75.00',
            'duration_hours': 3,
            'is_active': True
        }
        
        response = self.client.post(reverse('service-list'), service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        service_id = response.data['id']
        
        # Customer views service
        self.client.force_authenticate(user=self.client_user)
        
        response = self.client.get(reverse('service-detail', args=[service_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'House Cleaning Service')

    def test_messaging_workflow(self):
        """Test messaging system workflow"""
        self.client.force_authenticate(user=self.client_user)
        
        # Create conversation
        conversation_data = {
            'title': 'Project Discussion',
            'participants': [self.worker_user.id]
        }
        
        response = self.client.post(reverse('conversation-list'), conversation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation_id = response.data['id']
        
        # Send message
        message_data = {
            'conversation': conversation_id,
            'content': 'Hello, let\'s discuss the project details.'
        }
        
        response = self.client.post(reverse('message-list'), message_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Worker replies
        self.client.force_authenticate(user=self.worker_user)
        
        reply_data = {
            'conversation': conversation_id,
            'content': 'Sure, I\'m ready to discuss.'
        }
        
        response = self.client.post(reverse('message-list'), reply_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify conversation has messages
        response = self.client.get(reverse('conversation-detail', args=[conversation_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_workflow(self):
        """Test payment system workflow"""
        # Create a job first
        self.client.force_authenticate(user=self.client_user)
        
        job = Job.objects.create(
            client=self.client_user,
            title='Payment Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.IN_PROGRESS
        )
        
        # Create payment method
        payment_method_data = {
            'type': 'CREDIT_CARD',
            'provider': 'VISA',
            'last_four': '1234',
            'is_default': True
        }
        
        response = self.client.post(reverse('paymentmethod-list'), payment_method_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Create payment
        payment_data = {
            'job': job.id,
            'recipient': self.worker_user.id,
            'amount': '100.00',
            'status': 'PENDING'
        }
        
        response = self.client.post(reverse('payment-list'), payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment_id = response.data['id']
        
        # Update payment status
        update_data = {'status': 'COMPLETED'}
        response = self.client.patch(reverse('payment-detail', args=[payment_id]), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rating_workflow(self):
        """Test rating system workflow"""
        # Create completed job
        job = Job.objects.create(
            client=self.client_user,
            title='Rating Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.COMPLETED
        )
        
        self.client.force_authenticate(user=self.client_user)
        
        # Create rating
        rating_data = {
            'job': job.id,
            'rated_user': self.worker_user.id,
            'rating': 5,
            'comment': 'Excellent work!'
        }
        
        response = self.client.post(reverse('rating-list'), rating_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify rating was created
        response = self.client.get(reverse('rating-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_permissions_and_security(self):
        """Test API permissions and security"""
        # Test unauthenticated access
        response = self.client.get(reverse('job-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test authenticated access
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(reverse('job-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test unauthorized access to other user's data
        other_user_job = Job.objects.create(
            client=self.worker_user,
            title='Other User Job',
            budget=Decimal('50.00'),
            max_workers=1,
            status=Job.Status.OPEN
        )
        
        # Client should not be able to edit worker's job
        response = self.client.patch(reverse('job-detail', args=[other_user_job.id]), 
                                   {'title': 'Hacked Job'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_error_handling(self):
        """Test API error handling"""
        self.client.force_authenticate(user=self.client_user)
        
        # Test invalid data
        invalid_job_data = {
            'title': '',  # Empty title should fail validation
            'budget': -100,  # Negative budget should fail
            'max_workers': 0  # Zero workers should fail
        }
        
        response = self.client.post(reverse('job-list'), invalid_job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test non-existent resource
        response = self.client.get(reverse('job-detail', args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')

class DeploymentReadinessTests(TestCase):
    """
    Tests to verify deployment readiness
    """
    
    def test_database_connectivity(self):
        """Test database connectivity"""
        # Create a simple model instance to test DB connection
        user = User.objects.create_user(
            email='dbtest@example.com',
            password='TestPass123!'
        )
        self.assertIsNotNone(user.id)
        
        # Test query
        retrieved_user = User.objects.get(email='dbtest@example.com')
        self.assertEqual(user.id, retrieved_user.id)

    def test_model_relationships(self):
        """Test model relationships work correctly"""
        # Create related objects
        client = User.objects.create_user(
            email='client@example.com',
            password='TestPass123!',
            role='CLIENT'
        )
        
        worker = User.objects.create_user(
            email='worker@example.com',
            password='TestPass123!',
            role='WORKER'
        )
        
        job = Job.objects.create(
            client=client,
            title='Relationship Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.OPEN
        )
        
        application = JobApplication.objects.create(
            job=job,
            worker=worker,
            cover_letter='Test application'
        )
        
        # Test relationships
        self.assertEqual(job.client, client)
        self.assertEqual(application.job, job)
        self.assertEqual(application.worker, worker)
        self.assertEqual(job.applications.first(), application)

    def test_serializers_work(self):
        """Test that serializers work correctly"""
        from accounts.serializers import CustomUserSerializer
        from jobs.serializers import JobSerializer
        
        user = User.objects.create_user(
            email='serializer@example.com',
            password='TestPass123!'
        )
        
        # Test user serializer
        user_serializer = CustomUserSerializer(user)
        self.assertIn('email', user_serializer.data)
        self.assertEqual(user_serializer.data['email'], 'serializer@example.com')
        
        # Test job serializer
        job = Job.objects.create(
            client=user,
            title='Serializer Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.OPEN
        )
        
        job_serializer = JobSerializer(job)
        self.assertIn('title', job_serializer.data)
        self.assertEqual(job_serializer.data['title'], 'Serializer Test Job')

    def test_url_patterns(self):
        """Test that URL patterns are correctly configured"""
        from django.urls import reverse, NoReverseMatch
        
        # Test that all major URL patterns exist
        url_names = [
            'auth-register',
            'auth-login',
            'auth-logout',
            'auth-me',
            'job-list',
            'service-list',
            'conversation-list',
            'message-list',
            'payment-list',
            'rating-list',
            'health-check'
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except NoReverseMatch:
                self.fail(f"URL pattern '{url_name}' not found")

    def test_settings_configuration(self):
        """Test that settings are properly configured for deployment"""
        from django.conf import settings
        
        # Test that required settings exist
        required_settings = [
            'SECRET_KEY',
            'DATABASES',
            'INSTALLED_APPS',
            'REST_FRAMEWORK',
            'SIMPLE_JWT'
        ]
        
        for setting_name in required_settings:
            self.assertTrue(hasattr(settings, setting_name), 
                          f"Required setting '{setting_name}' not found")
        
        # Test that Django REST Framework is configured
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        self.assertIn('rest_framework_simplejwt', settings.INSTALLED_APPS)
        
        # Test that custom apps are installed
        custom_apps = [
            'accounts',
            'core',
            'jobs',
            'services',
            'messaging',
            'payments',
            'ratings',
            'notifications'
        ]
        
        for app in custom_apps:
            self.assertIn(app, settings.INSTALLED_APPS, 
                         f"Custom app '{app}' not in INSTALLED_APPS")
