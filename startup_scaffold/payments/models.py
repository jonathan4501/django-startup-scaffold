import uuid
from django.db import models
from django.conf import settings

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    shift = models.ForeignKey('shifts.Shift', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD', choices=[
        ('USD', 'US Dollar'),
        ('XOF', 'West African CFA Franc'),
        ('NGN', 'Nigerian Naira'),
        ('GHS', 'Ghanaian Cedi'),
        ('MOMO', 'Mobile Money'),
    ])
    payment_method = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50, blank=True, null=True)  # e.g. 'flutterwave', 'paystack', 'tmoney', 'flooz'
    status = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Status transition timestamps
    initiated_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"
