from django.contrib import admin
from .models import Shift

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'worker', 'start_time', 'end_time', 'status', 'is_confirmed')
    list_filter = ('status', 'is_confirmed')
    search_fields = ('name', 'worker__email')
