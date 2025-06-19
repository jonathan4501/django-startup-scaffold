from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIQueryViewSet

router = DefaultRouter()
router.register(r'', AIQueryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
