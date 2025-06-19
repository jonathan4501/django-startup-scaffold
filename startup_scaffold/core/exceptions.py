from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response

class CustomAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'
    default_code = 'error'

class ValidationException(CustomAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Validation error.'
    default_code = 'validation_error'

def raise_validation_error(detail):
    raise ValidationException(detail=detail)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'status': 'error',
            'message': '',
            'data': {},
            'errors': [],
        }

        if isinstance(exc, ValidationException):
            custom_response_data['message'] = str(exc.detail)
            custom_response_data['errors'] = exc.detail if isinstance(exc.detail, list) else [str(exc.detail)]
        else:
            custom_response_data['message'] = response.data.get('detail', '')
            custom_response_data['errors'] = [response.data] if not isinstance(response.data, list) else response.data

        response.data = custom_response_data

    return response
