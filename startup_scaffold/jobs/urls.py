from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, SkillViewSet, LocationViewSet, JobApplicationViewSet, JobRecommendationViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'applications', JobApplicationViewSet, basename='application')
router.register(r'recommendations', JobRecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
]
