from django.contrib import admin
from .models import Attendance, DailyAttendanceReport

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'shift', 'check_in', 'check_out', 'device_type')
    list_filter = ('check_in', 'check_out', 'device_type', 'user')
    search_fields = ('user__username', 'user__email')

@admin.register(DailyAttendanceReport)
class DailyAttendanceReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'total_worked_hours', 'was_late', 'was_absent')
    list_filter = ('date', 'was_late', 'was_absent', 'user')
    search_fields = ('user__username', 'user__email')
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    export_as_csv.short_description = "Export Selected as CSV"
