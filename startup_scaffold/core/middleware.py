import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import activate
from django.conf import settings
import uuid

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.id = str(uuid.uuid4())
        logger.info(f"Request {request.id}: {request.method} {request.get_full_path()}")

    def process_response(self, request, response):
        request_id = getattr(request, 'id', 'unknown')
        logger.info(f"Response {request_id}: Status {response.status_code}")
        return response

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Example: activate timezone from user profile or default
        activate(settings.TIME_ZONE)

class CorrelationIdMiddleware(MiddlewareMixin):
    def process_request(self, request):
        correlation_id = request.headers.get('X-Correlation-ID')
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        request.correlation_id = correlation_id
        logger.info(f"Correlation ID: {correlation_id}")
