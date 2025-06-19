from rest_framework import viewsets
from .models import Customer, CustomerInteraction
from .serializers import CustomerSerializer, CustomerInteractionSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCustomerOwnerOrAdmin

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsCustomerOwnerOrAdmin]

class CustomerInteractionViewSet(viewsets.ModelViewSet):
    queryset = CustomerInteraction.objects.all()
    serializer_class = CustomerInteractionSerializer
    permission_classes = [IsAuthenticated, IsCustomerOwnerOrAdmin]
