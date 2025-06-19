from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from .serializers import PaymentSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    @csrf_exempt
    def webhook_flutterwave(self, request):
        # Placeholder for Flutterwave webhook listener
        # Process webhook data, verify signature, update payment status
        return Response({"detail": "Flutterwave webhook received"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    @csrf_exempt
    def webhook_paystack(self, request):
        # Placeholder for Paystack webhook listener
        # Process webhook data, verify signature, update payment status
        return Response({"detail": "Paystack webhook received"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    @csrf_exempt
    def webhook_tmoney(self, request):
        # Placeholder for T-money webhook listener
        return Response({"detail": "T-money webhook received"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    @csrf_exempt
    def webhook_flooz(self, request):
        # Placeholder for Flooz webhook listener
        return Response({"detail": "Flooz webhook received"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def verify_transaction(self, request):
        transaction_id = request.query_params.get('transaction_id')
        if not transaction_id:
            return Response({"error": "transaction_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

# Placeholder for Paystack and Flutterwave integration scaffolds
# These can be expanded with actual integration logic as needed
