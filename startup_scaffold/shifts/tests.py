from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Shift
from django.contrib.auth import get_user_model

User = get_user_model()

class ShiftTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.job = None
        # Create a job if needed for FK, or mock it
        from jobs.models import Job
        self.job = Job.objects.create(name='Test Job')

    def test_shift_conflict_validation(self):
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        shift1 = Shift.objects.create(job=self.job, worker=self.user, name='Shift 1', start_time=start_time, end_time=end_time)
        # Attempt to create overlapping shift
        data = {
            'job': self.job.id,
            'worker': self.user.id,
            'name': 'Shift 2',
            'start_time': start_time + timedelta(minutes=30),
            'end_time': end_time + timedelta(hours=1),
        }
        response = self.client.post(reverse('shift-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('overlaps', str(response.data).lower())

    def test_check_in_with_geolocation(self):
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        shift = Shift.objects.create(job=self.job, worker=self.user, name='Shift', start_time=start_time, end_time=end_time)
        url = reverse('shift-check-in', args=[shift.id])
        data = {
            'check_in': timezone.now().isoformat(),
            'check_in_lat': 40.7128,
            'check_in_lng': -74.0060,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        

    def test_missed_shift_marking(self):
        start_time = timezone.now() - timedelta(minutes=20)
        end_time = start_time + timedelta(hours=2)
        shift = Shift.objects.create(job=self.job, worker=self.user, name='Shift', start_time=start_time, end_time=end_time, is_confirmed=True)
        # Run the task manually
        from .tasks import mark_missed_shifts
        mark_missed_shifts()
        shift.refresh_from_db()
        self.assertEqual(shift.status, 'missed')

    def test_calendar_endpoint(self):
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=3)
        shift = Shift.objects.create(job=self.job, worker=self.user, name='Calendar Shift', start_time=start_time, end_time=end_time)
        url = reverse('shift-calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(event['title'] == 'Calendar Shift' for event in response.data))
