from django.contrib import admin
from .models import Customer, CustomerInteraction

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'lead_status', 'potential_revenue', 'job', 'created_at')
    list_filter = ('lead_status',)
    search_fields = ('name', 'email', 'phone')

@admin.register(CustomerInteraction)
class CustomerInteractionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'interaction_type', 'timestamp')
    list_filter = ('interaction_type',)
    search_fields = ('customer__name', 'notes')
