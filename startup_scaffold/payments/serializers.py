from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'user', 'shift', 'amount', 'currency', 'payment_method', 'payment_type', 'status', 'transaction_id', 'created_at', 'updated_at', 'initiated_at', 'verified_at', 'failed_at')
