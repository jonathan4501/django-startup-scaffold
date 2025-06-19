from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, submit_review_for_job

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

from django.urls import path

urlpatterns = router.urls + [
    path('jobs/<uuid:job_id>/review/', submit_review_for_job, name='submit-review-for-job'),
]
