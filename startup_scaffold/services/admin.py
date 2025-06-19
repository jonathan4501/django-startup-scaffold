from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_active', 'is_public', 'created_at')
    search_fields = ('name', 'description')
