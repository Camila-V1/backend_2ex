import logging

logger = logging.getLogger(__name__)

class URLDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log antes del request
        logger.info(f"🌐 REQUEST: {request.method} {request.path}")
        logger.info(f"🌐 Full path: {request.get_full_path()}")
        
        response = self.get_response(request)
        
        # Log después del response
        logger.info(f"🌐 RESPONSE: {response.status_code} for {request.path}")
        
        return response
