from rest_framework.response import Response

class BaseAPIViewResponse(Response):
    def __init__(self, data=None, status=None, message=None, errors=None, **kwargs):
        response_data = {
            'status': status if status is not None else 'success',
            'message': message if message else '',
            'data': data if data is not None else {},
            'errors': errors if errors else [],
        }
        super().__init__(response_data, **kwargs)
