from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Payment, PaymentMethod, Transaction
from jobs.models import Job
from .serializers import PaymentSerializer, PaymentMethodSerializer, TransactionSerializer

User = get_user_model()

class PaymentModelTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='TestPass123!',
            role='CLIENT'
        )
        self.worker_user = User.objects.create_user(
            email='worker@example.com',
            password='TestPass123!',
            role='WORKER'
        )
        self.job = Job.objects.create(
            client=self.client_user,
            title='Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.OPEN
        )

    def test_payment_creation(self):
        """Test payment model creation"""
        payment = Payment.objects.create(
            job=self.job,
            payer=self.client_user,
            recipient=self.worker_user,
            amount=Decimal('100.00'),
            status='PENDING'
        )
        
        self.assertEqual(payment.job, self.job)
        self.assertEqual(payment.payer, self.client_user)
        self.assertEqual(payment.recipient, self.worker_user)
        self.assertEqual(payment.amount, Decimal('100.00'))
        self.assertEqual(payment.status, 'PENDING')

    def test_payment_str_method(self):
        """Test payment string representation"""
        payment = Payment.objects.create(
            job=self.job,
            payer=self.client_user,
            recipient=self.worker_user,
            amount=Decimal('100.00'),
            status='PENDING'
        )
        expected_str = f"Payment of ${payment.amount} from {self.client_user.email} to {self.worker_user.email}"
        self.assertEqual(str(payment), expected_str)

    def test_payment_amount_validation(self):
        """Test payment amount validation"""
        # Test negative amount
        with self.assertRaises(Exception):
            payment = Payment(
                job=self.job,
                payer=self.client_user,
                recipient=self.worker_user,
                amount=Decimal('-10.00'),
                status='PENDING'
            )
            payment.full_clean()

    def test_payment_status_choices(self):
        """Test payment status choices"""
        valid_statuses = ['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED']
        for status in valid_statuses:
            payment = Payment.objects.create(
                job=self.job,
                payer=self.client_user,
                recipient=self.worker_user,
                amount=Decimal('100.00'),
                status=status
            )
            self.assertEqual(payment.status, status)

class PaymentMethodModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )

    def test_payment_method_creation(self):
        """Test payment method model creation"""
        payment_method = PaymentMethod.objects.create(
            user=self.user,
            type='CREDIT_CARD',
            provider='VISA',
            last_four='1234',
            is_default=True
        )
        
        self.assertEqual(payment_method.user, self.user)
        self.assertEqual(payment_method.type, 'CREDIT_CARD')
        self.assertEqual(payment_method.provider, 'VISA')
        self.assertEqual(payment_method.last_four, '1234')
        self.assertTrue(payment_method.is_default)

    def test_payment_method_str_method(self):
        """Test payment method string representation"""
        payment_method = PaymentMethod.objects.create(
            user=self.user,
            type='CREDIT_CARD',
            provider='VISA',
            last_four='1234'
        )
        expected_str = f"{payment_method.provider} ending in {payment_method.last_four}"
        self.assertEqual(str(payment_method), expected_str)

    def test_only_one_default_payment_method(self):
        """Test that only one payment method can be default per user"""
        # Create first default payment method
        payment_method1 = PaymentMethod.objects.create(
            user=self.user,
            type='CREDIT_CARD',
            provider='VISA',
            last_four='1234',
            is_default=True
        )
        
        # Create second default payment method
        payment_method2 = PaymentMethod.objects.create(
            user=self.user,
            type='CREDIT_CARD',
            provider='MASTERCARD',
            last_four='5678',
            is_default=True
        )
        
        # First payment method should no longer be default
        payment_method1.refresh_from_db()
        self.assertFalse(payment_method1.is_default)
        self.assertTrue(payment_method2.is_default)

class TransactionModelTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='TestPass123!',
            role='CLIENT'
        )
        self.worker_user = User.objects.create_user(
            email='worker@example.com',
            password='TestPass123!',
            role='WORKER'
        )
        self.job = Job.objects.create(
            client=self.client_user,
            title='Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.OPEN
        )
        self.payment = Payment.objects.create(
            job=self.job,
            payer=self.client_user,
            recipient=self.worker_user,
            amount=Decimal('100.00'),
            status='PENDING'
        )

    def test_transaction_creation(self):
        """Test transaction model creation"""
        transaction = Transaction.objects.create(
            payment=self.payment,
            transaction_id='txn_123456789',
            amount=Decimal('100.00'),
            status='SUCCESS',
            gateway='STRIPE'
        )
        
        self.assertEqual(transaction.payment, self.payment)
        self.assertEqual(transaction.transaction_id, 'txn_123456789')
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.status, 'SUCCESS')
        self.assertEqual(transaction.gateway, 'STRIPE')

    def test_transaction_str_method(self):
        """Test transaction string representation"""
        transaction = Transaction.objects.create(
            payment=self.payment,
            transaction_id='txn_123456789',
            amount=Decimal('100.00'),
            status='SUCCESS',
            gateway='STRIPE'
        )
        expected_str = f"Transaction {transaction.transaction_id} - {transaction.status}"
        self.assertEqual(str(transaction), expected_str)

class PaymentAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='TestPass123!',
            role='CLIENT'
        )
        self.worker_user = User.objects.create_user(
            email='worker@example.com',
            password='TestPass123!',
            role='WORKER'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPass123!'
        )
        
        self.job = Job.objects.create(
            client=self.client_user,
            title='Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.OPEN
        )
        
        self.payment = Payment.objects.create(
            job=self.job,
            payer=self.client_user,
            recipient=self.worker_user,
            amount=Decimal('100.00'),
            status='PENDING'
        )
        
        self.payment_list_url = reverse('payment-list')
        self.payment_detail_url = reverse('payment-detail', args=[self.payment.id])

    def test_list_payments_authenticated(self):
        """Test listing payments for authenticated user"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(self.payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_payments_unauthenticated(self):
        """Test listing payments for unauthenticated user"""
        response = self.client.get(self.payment_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_payment(self):
        """Test creating a new payment"""
        self.client.force_authenticate(user=self.client_user)
        data = {
            'job': self.job.id,
            'recipient': self.worker_user.id,
            'amount': '50.00',
            'status': 'PENDING'
        }
        response = self.client.post(self.payment_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 2)

    def test_retrieve_payment_as_payer(self):
        """Test retrieving payment as payer"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(self.payment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '100.00')

    def test_retrieve_payment_as_recipient(self):
        """Test retrieving payment as recipient"""
        self.client.force_authenticate(user=self.worker_user)
        response = self.client.get(self.payment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '100.00')

    def test_retrieve_payment_as_unauthorized_user(self):
        """Test retrieving payment as unauthorized user"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.payment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_payment_status(self):
        """Test updating payment status"""
        self.client.force_authenticate(user=self.client_user)
        data = {'status': 'COMPLETED'}
        response = self.client.patch(self.payment_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'COMPLETED')

class PaymentMethodAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPass123!'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            user=self.user,
            type='CREDIT_CARD',
            provider='VISA',
            last_four='1234',
            is_default=True
        )
        
        self.payment_method_list_url = reverse('paymentmethod-list')
        self.payment_method_detail_url = reverse('paymentmethod-detail', args=[self.payment_method.id])

    def test_list_payment_methods_authenticated(self):
        """Test listing payment methods for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.payment_method_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_payment_methods_unauthenticated(self):
        """Test listing payment methods for unauthenticated user"""
        response = self.client.get(self.payment_method_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_payment_method(self):
        """Test creating a new payment method"""
        self.client.force_authenticate(user=self.user)
        data = {
            'type': 'CREDIT_CARD',
            'provider': 'MASTERCARD',
            'last_four': '5678',
            'is_default': False
        }
        response = self.client.post(self.payment_method_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentMethod.objects.filter(user=self.user).count(), 2)

    def test_retrieve_payment_method_as_owner(self):
        """Test retrieving payment method as owner"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.payment_method_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['provider'], 'VISA')

    def test_retrieve_payment_method_as_non_owner(self):
        """Test retrieving payment method as non-owner"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.payment_method_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_payment_method(self):
        """Test updating payment method"""
        self.client.force_authenticate(user=self.user)
        data = {'is_default': False}
        response = self.client.patch(self.payment_method_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.payment_method.refresh_from_db()
        self.assertFalse(self.payment_method.is_default)

    def test_delete_payment_method(self):
        """Test deleting payment method"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.payment_method_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PaymentMethod.objects.filter(user=self.user).count(), 0)

class TransactionAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='TestPass123!',
            role='CLIENT'
        )
        self.worker_user = User.objects.create_user(
            email='worker@example.com',
            password='TestPass123!',
            role='WORKER'
        )
        
        self.job = Job.objects.create(
            client=self.client_user,
            title='Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.OPEN
        )
        
        self.payment = Payment.objects.create(
            job=self.job,
            payer=self.client_user,
            recipient=self.worker_user,
            amount=Decimal('100.00'),
            status='PENDING'
        )
        
        self.transaction = Transaction.objects.create(
            payment=self.payment,
            transaction_id='txn_123456789',
            amount=Decimal('100.00'),
            status='SUCCESS',
            gateway='STRIPE'
        )
        
        self.transaction_list_url = reverse('transaction-list')
        self.transaction_detail_url = reverse('transaction-detail', args=[self.transaction.id])

    def test_list_transactions_authenticated(self):
        """Test listing transactions for authenticated user"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(self.transaction_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_transaction(self):
        """Test retrieving transaction details"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(self.transaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction_id'], 'txn_123456789')
        self.assertEqual(response.data['status'], 'SUCCESS')

class PaymentSerializerTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='TestPass123!',
            role='CLIENT'
        )
        self.worker_user = User.objects.create_user(
            email='worker@example.com',
            password='TestPass123!',
            role='WORKER'
        )
        self.job = Job.objects.create(
            client=self.client_user,
            title='Test Job',
            budget=Decimal('100.00'),
            max_workers=1,
            status=Job.Status.OPEN
        )

    def test_payment_serializer(self):
        """Test payment serializer"""
        payment = Payment.objects.create(
            job=self.job,
            payer=self.client_user,
            recipient=self.worker_user,
            amount=Decimal('100.00'),
            status='PENDING'
        )
        
        serializer = PaymentSerializer(payment)
        data = serializer.data
        
        self.assertEqual(data['amount'], '100.00')
        self.assertEqual(data['status'], 'PENDING')
        self.assertEqual(data['payer'], self.client_user.id)
        self.assertEqual(data['recipient'], self.worker_user.id)

    def test_payment_method_serializer(self):
        """Test payment method serializer"""
        payment_method = PaymentMethod.objects.create(
            user=self.client_user,
            type='CREDIT_CARD',
            provider='VISA',
            last_four='1234',
            is_default=True
        )
        
        serializer = PaymentMethodSerializer(payment_method)
        data = serializer.data
        
        self.assertEqual(data['type'], 'CREDIT_CARD')
        self.assertEqual(data['provider'], 'VISA')
        self.assertEqual(data['last_four'], '1234')
        self.assertTrue(data['is_default'])

    def test_transaction_serializer(self):
        """Test transaction serializer"""
        payment = Payment.objects.create(
            job=self.job,
            payer=self.client_user,
            recipient=self.worker_user,
            amount=Decimal('100.00'),
            status='PENDING'
        )
        
        transaction = Transaction.objects.create(
            payment=payment,
            transaction_id='txn_123456789',
            amount=Decimal('100.00'),
            status='SUCCESS',
            gateway='STRIPE'
        )
        
        serializer = TransactionSerializer(transaction)
        data = serializer.data
        
        self.assertEqual(data['transaction_id'], 'txn_123456789')
        self.assertEqual(data['amount'], '100.00')
        self.assertEqual(data['status'], 'SUCCESS')
        self.assertEqual(data['gateway'], 'STRIPE')
