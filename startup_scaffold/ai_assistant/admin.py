from django.contrib import admin
from .models import AIQuery

@admin.register(AIQuery)
class AIQueryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query_text', 'created_at')
    search_fields = ('query_text', 'response_text', 'user__email')
    list_filter = ('created_at',)

