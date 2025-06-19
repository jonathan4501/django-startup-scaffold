from rest_framework import serializers
from .models import Shift
from django.utils.timezone import make_aware
from django.utils import timezone

class ShiftSerializer(serializers.ModelSerializer):
    duration = serializers.ReadOnlyField()
    notes = serializers.CharField(required=False, allow_blank=True)
    worker_feedback = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Shift
        fields = ('id', 'job', 'worker', 'name', 'start_time', 'end_time', 'is_confirmed', 'is_completed', 'status', 'notes', 'worker_feedback', 'duration', 'created_at', 'updated_at')

    def validate(self, data):
        # Ensure start_time and end_time are timezone-aware
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        if start_time and timezone.is_naive(start_time):
            data['start_time'] = make_aware(start_time)
        if end_time and timezone.is_naive(end_time):
            data['end_time'] = make_aware(end_time)

        # Validate shift conflict
        worker = data.get('worker') or getattr(self.instance, 'worker', None)
        start_time = data.get('start_time') or getattr(self.instance, 'start_time', None)
        end_time = data.get('end_time') or getattr(self.instance, 'end_time', None)

        if worker and start_time and end_time:
            overlapping = Shift.objects.filter(
                worker=worker,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance:
                overlapping = overlapping.exclude(id=self.instance.id)
            if overlapping.exists():
                raise serializers.ValidationError("This shift overlaps with another scheduled shift.")
        return data

