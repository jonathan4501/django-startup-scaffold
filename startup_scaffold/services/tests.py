from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Service, ServiceCategory, ServiceBooking

User = get_user_model()

class ServiceCategoryModelTests(TestCase):
    def test_service_category_creation(self):
        """Test service category model creation"""
        category = ServiceCategory.objects.create(
            name='Home Cleaning',
            description='Professional home cleaning services',
            is_active=True
        )
        
        self.assertEqual(category.name, 'Home Cleaning')
        self.assertEqual(category.description, 'Professional home cleaning services')
        self.assertTrue(category.is_active)

    def test_service_category_str_method(self):
        """Test service category string representation"""
        category = ServiceCategory.objects.create(
            name='Home Cleaning',
            description='Professional home cleaning services'
        )
        self.assertEqual(str(category), 'Home Cleaning')

class ServiceModelTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='TestPass123!',
            role='SERVICE_PROVIDER'
        )
        self.category = ServiceCategory.objects.create(
            name='Home Cleaning',
            description='Professional home cleaning services'
        )

    def test_service_creation(self):
        """Test service model creation"""
        service = Service.objects.create(
            provider=self.provider,
            category=self.category,
            title='Professional House Cleaning',
            description='Complete house cleaning service',
            price=Decimal('50.00'),
            duration_hours=2,
            is_active=True
        )
        
        self.assertEqual(service.provider, self.provider)
        self.assertEqual(service.category, self.category)
        self.assertEqual(service.title, 'Professional House Cleaning')
        self.assertEqual(service.price, Decimal('50.00'))
        self.assertEqual(service.duration_hours, 2)
        self.assertTrue(service.is_active)

    def test_service_str_method(self):
        """Test service string representation"""
        service = Service.objects.create(
            provider=self.provider,
            category=self.category,
            title='Professional House Cleaning',
            description='Complete house cleaning service',
            price=Decimal('50.00'),
            duration_hours=2
        )
        self.assertEqual(str(service), 'Professional House Cleaning')

class ServiceAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider = User.objects.create_user(
            email='provider@example.com',
            password='TestPass123!',
            role='SERVICE_PROVIDER'
        )
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='TestPass123!',
            role='CUSTOMER'
        )
        self.category = ServiceCategory.objects.create(
            name='Home Cleaning',
            description='Professional home cleaning services'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            category=self.category,
            title='Professional House Cleaning',
            description='Complete house cleaning service',
            price=Decimal('50.00'),
            duration_hours=2,
            is_active=True
        )
        
        self.service_list_url = reverse('service-list')
        self.service_detail_url = reverse('service-detail', args=[self.service.id])

    def test_list_services_authenticated(self):
        """Test listing services for authenticated user"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.service_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_services_unauthenticated(self):
        """Test listing services for unauthenticated user"""
        response = self.client.get(self.service_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_service_as_provider(self):
        """Test creating a service as provider"""
        self.client.force_authenticate(user=self.provider)
        data = {
            'category': self.category.id,
            'title': 'Deep Cleaning Service',
            'description': 'Comprehensive deep cleaning',
            'price': '75.00',
            'duration_hours': 3,
            'is_active': True
        }
        response = self.client.post(self.service_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 2)

    def test_retrieve_service(self):
        """Test retrieving service details"""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.service_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Professional House Cleaning')

    def test_update_service_as_provider(self):
        """Test updating service as provider"""
        self.client.force_authenticate(user=self.provider)
        data = {'price': '60.00'}
        response = self.client.patch(self.service_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.service.refresh_from_db()
        self.assertEqual(self.service.price, Decimal('60.00'))

    def test_update_service_as_non_provider(self):
        """Test updating service as non-provider"""
        self.client.force_authenticate(user=self.customer)
        data = {'price': '60.00'}
        response = self.client.patch(self.service_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_service_as_provider(self):
        """Test deleting service as provider"""
        self.client.force_authenticate(user=self.provider)
        response = self.client.delete(self.service_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Service.objects.count(), 0)

class ServiceCategoryAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!'
        )
        self.category = ServiceCategory.objects.create(
            name='Home Cleaning',
            description='Professional home cleaning services',
            is_active=True
        )
        
        self.category_list_url = reverse('servicecategory-list')
        self.category_detail_url = reverse('servicecategory-detail', args=[self.category.id])

    def test_list_categories_authenticated(self):
        """Test listing categories for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_category_as_admin(self):
        """Test creating category as admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'Plumbing',
            'description': 'Professional plumbing services',
            'is_active': True
        }
        response = self.client.post(self.category_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceCategory.objects.count(), 2)

    def test_create_category_as_regular_user(self):
        """Test creating category as regular user"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Plumbing',
            'description': 'Professional plumbing services',
            'is_active': True
        }
        response = self.client.post(self.category_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_category(self):
        """Test retrieving category details"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Home Cleaning')

    def test_update_category_as_admin(self):
        """Test updating category as admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'description': 'Updated description'}
        response = self.client.patch(self.category_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.category.refresh_from_db()
        self.assertEqual(self.category.description, 'Updated description')
