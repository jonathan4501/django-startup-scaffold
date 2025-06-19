from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Review
from jobs.models import Job

User = get_user_model()

class ReviewTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(email='client@example.com', password='pass')
        self.worker_user = User.objects.create_user(email='worker@example.com', password='pass')
        self.other_user = User.objects.create_user(email='other@example.com', password='pass')

        self.job = Job.objects.create(worker=self.worker_user, client=self.client_user, status='completed')

        self.client = APIClient()
        self.client.login(email='client@example.com', password='pass')

    def test_submit_review_for_job(self):
        url = reverse('submit-review-for-job', kwargs={'job_id': self.job.id})
        data = {
            'rating': 4.5,
            'title': 'Great job',
            'content': 'Very professional and timely.',
            'is_anonymous': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.reviewer, self.client_user)
        self.assertEqual(review.reviewee, self.worker_user)
        self.assertEqual(review.job, self.job)

    def test_prevent_self_review(self):
        self.client.login(email='worker@example.com', password='pass')
        url = reverse('submit-review-for-job', kwargs={'job_id': self.job.id})
        data = {
            'rating': 5,
            'title': 'Self review',
            'content': 'Trying to review myself',
            'is_anonymous': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_average_rating_endpoint(self):
        Review.objects.create(reviewer=self.client_user, reviewee=self.worker_user, job=self.job, rating=4.0)
        Review.objects.create(reviewer=self.other_user, reviewee=self.worker_user, job=self.job, rating=5.0)

        url = reverse('review-average-rating', kwargs={'user_id': self.worker_user.id})
        self.client.login(email='client@example.com', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(response.data['average_rating'], 4.5)

    def test_reviews_received_endpoint(self):
        Review.objects.create(reviewer=self.client_user, reviewee=self.worker_user, job=self.job, rating=4.0)
        Review.objects.create(reviewer=self.other_user, reviewee=self.worker_user, job=self.job, rating=5.0)

        url = reverse('review-reviews-received', kwargs={'user_id': self.worker_user.id})
        self.client.login(email='client@example.com', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
