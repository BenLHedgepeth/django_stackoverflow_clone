
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled

def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, Throttled):
        too_many_requests = {'detail': "Vote has been throttled"}
        response.data = too_many_requests
    return response
