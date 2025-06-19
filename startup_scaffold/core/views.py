from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class HealthCheckView(APIView):
    """
    Health check endpoint to verify database connectivity and basic app health.
    """

    def get(self, request):
        try:
            # Simple query to check DB connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
            if row is None:
                raise Exception("Database query returned no results")
            return Response({"status": "ok", "message": "Healthy"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
