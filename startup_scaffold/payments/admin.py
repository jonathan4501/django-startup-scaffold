from django.contrib import admin
from .models import Payment
import csv
from django.http import HttpResponse

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'shift', 'amount', 'currency', 'payment_method', 'payment_type', 'status', 'created_at')
    list_filter = ('payment_method', 'payment_type', 'status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'user__email')
    ordering = ('-created_at',)

    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=payments.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response

    export_as_csv.short_description = "Export Selected as CSV"
