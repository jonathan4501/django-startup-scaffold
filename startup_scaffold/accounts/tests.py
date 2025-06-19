from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.logout_url = reverse('auth-logout')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'WORKER',
            'phone_number': '+1234567890',
            'address': '123 Test St',
            'skills': ['Python', 'Django'],
            'availability': 'FULL_TIME'
        }

    def test_user_registration(self):
        """Test user registration with valid data"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, 'test@example.com')

    def test_user_registration_invalid_password(self):
        """Test user registration with non-matching passwords"""
        self.user_data['password2'] = 'DifferentPass123!'
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 0)

    def test_user_login(self):
        """Test user login with valid credentials"""
        # Create a user first
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        login_data = {
            'email': 'test@example.com',
            'password': 'WrongPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout(self):
        """Test user logout"""
        # Create and login user
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=user)
        
        # Get refresh token
        login_response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }, format='json')
        
        # Logout
        response = self.client.post(self.logout_url, {
            'refresh': login_response.data['refresh']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        self.password_reset_request_url = reverse('password-reset-request')
        self.password_reset_confirm_url = reverse('password-reset-confirm')

    def test_password_reset_request(self):
        """Test password reset request with valid email"""
        response = self.client.post(self.password_reset_request_url, {
            'email': 'test@example.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request_invalid_email(self):
        """Test password reset request with invalid email"""
        response = self.client.post(self.password_reset_request_url, {
            'email': 'nonexistent@example.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        # Generate token and uid
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        response = self.client.post(self.password_reset_confirm_url, {
            'uid': uid,
            'token': token,
            'new_password': 'NewTestPass123!',
            'new_password2': 'NewTestPass123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password works
        login_response = self.client.post(reverse('auth-login'), {
            'email': 'test@example.com',
            'password': 'NewTestPass123!'
        }, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

class EmailVerificationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        self.send_verification_url = reverse('send-verification-email')
        self.verify_email_url = reverse('email-verify')

    def test_send_verification_email(self):
        """Test sending verification email"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.send_verification_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_email(self):
        """Test email verification"""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        
        response = self.client.get(f'{self.verify_email_url}?uid={uid}&token={token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user is now verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

class UserAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_current_user(self):
        """Test retrieving current user information"""
        response = self.client.get(reverse('auth-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)

    def test_update_user_profile(self):
        """Test updating user profile"""
        url = reverse('user-detail', args=[self.user.id])
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+9876543210'
        }
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.phone_number, '+9876543210')
