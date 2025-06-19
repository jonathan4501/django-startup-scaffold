from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Shift
from .serializers import ShiftSerializer

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Shift.objects.all()
        return Shift.objects.filter(worker=user)

    @action(detail=False, methods=['get'], url_path='my')
    def my_shifts(self, request):
        user = request.user
        shifts = Shift.objects.filter(worker=user)
        serializer = self.get_serializer(shifts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='confirm')
    def confirm_shift(self, request, pk=None):
        shift = get_object_or_404(Shift, pk=pk, worker=request.user)
        shift.is_confirmed = True
        shift.save()
        serializer = self.get_serializer(shift)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='missed')
    def missed_shifts(self, request):
        user = request.user
        shifts = Shift.objects.filter(worker=user, status='missed')
        serializer = self.get_serializer(shifts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='calendar')
    def calendar(self, request):
        import icalendar
        from django.http import HttpResponse
        from datetime import datetime

        user = request.user
        if user.is_staff or user.is_superuser:
            shifts = Shift.objects.all()
        else:
            shifts = Shift.objects.filter(worker=user)

        cal = icalendar.Calendar()
        cal.add('prodid', '-//My Attendance App//mxm.dk//')
        cal.add('version', '2.0')

        for shift in shifts:
            event = icalendar.Event()
            event.add('summary', shift.name)
            event.add('dtstart', shift.start_time)
            event.add('dtend', shift.end_time)
            event.add('dtstamp', datetime.now())
            event['uid'] = f'shift-{shift.id}@myattendanceapp'
            cal.add_component(event)

        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename="shifts.ics"'
        return response
