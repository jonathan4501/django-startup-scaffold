from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

router = DefaultRouter()
router.register(r'', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/flutterwave/', PaymentViewSet.as_view({'post': 'webhook_flutterwave'}), name='webhook_flutterwave'),
    path('webhook/paystack/', PaymentViewSet.as_view({'post': 'webhook_paystack'}), name='webhook_paystack'),
    path('webhook/tmoney/', PaymentViewSet.as_view({'post': 'webhook_tmoney'}), name='webhook_tmoney'),
    path('webhook/flooz/', PaymentViewSet.as_view({'post': 'webhook_flooz'}), name='webhook_flooz'),
    path('verify-transaction/', PaymentViewSet.as_view({'get': 'verify_transaction'}), name='verify_transaction'),
]
