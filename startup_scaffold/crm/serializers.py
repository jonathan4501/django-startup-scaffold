from rest_framework import serializers
from .models import Customer, CustomerInteraction

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'user', 'name', 'email', 'phone', 'lead_status', 'potential_revenue', 'job', 'created_at', 'updated_at')

class CustomerInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInteraction
        fields = ('id', 'customer', 'interaction_type', 'notes', 'timestamp')
