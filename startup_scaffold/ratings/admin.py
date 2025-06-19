from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'reviewee', 'job', 'shift', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'job', 'shift')
    search_fields = ('title', 'content', 'reviewer__email', 'reviewee__email')
    ordering = ('-created_at',)
