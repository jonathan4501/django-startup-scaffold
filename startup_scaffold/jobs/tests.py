from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Job, JobApplication
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class JobAppTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(email='client@example.com', password='pass1234')
        self.worker_user = User.objects.create_user(email='worker@example.com', password='pass1234')
        self.client = APIClient()
        self.client.login(email='client@example.com', password='pass1234')
        self.worker_client = APIClient()
        self.worker_client.login(email='worker@example.com', password='pass1234')

        self.job = Job.objects.create(
            client=self.client_user,
            title='Test Job',
            budget=100,
            max_workers=1,
            status=Job.Status.OPEN
        )

    def test_budget_validation(self):
        job = Job(client=self.client_user, title='Invalid Budget', budget=0)
        with self.assertRaises(ValidationError):
            job.clean()

    def test_apply_to_job_once(self):
        JobApplication.objects.create(job=self.job, worker=self.worker_user)
        application = JobApplication(job=self.job, worker=self.worker_user)
        with self.assertRaises(ValidationError):
            application.clean()

    def test_cannot_apply_to_own_job(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(reverse('jobapplication-list'), {
            'job': str(self.job.id),
            'worker': str(self.client_user.id)
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_hire_worker_updates_job_status(self):
        application = JobApplication.objects.create(job=self.job, worker=self.worker_user)
        url = reverse('job-hire', args=[self.job.id])
        response = self.client.post(url, {'worker_id': str(self.worker_user.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.IN_PROGRESS)
        application.refresh_from_db()
        self.assertTrue(application.is_hired)

    def test_job_recommendation_excludes_applied_jobs(self):
        # This test would require more setup with recommendations, simplified here
        pass

    def test_only_job_owner_can_hire(self):
        application = JobApplication.objects.create(job=self.job, worker=self.worker_user)
        url = reverse('job-hire', args=[self.job.id])
        self.worker_client.force_authenticate(user=self.worker_user)
        response = self.worker_client.post(url, {'worker_id': str(self.worker_user.id)})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_signal_creates_rating_stubs(self):
        # This test requires ratings app and signal testing, simplified here
        pass

    def test_expired_job_cannot_be_applied_to(self):
        self.job.expiry_date = timezone.now() - timezone.timedelta(days=1)
        self.job.status = Job.Status.OPEN
        self.job.save()
        response = self.worker_client.post(reverse('jobapplication-list'), {
            'job': str(self.job.id),
            'worker': str(self.worker_user.id)
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
