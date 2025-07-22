# api/middleware.py
import logging
import time
from .models import OperationLog

logger = logging.getLogger(__name__)


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Process the request
        response = self.get_response(request)

        duration = time.time() - start_time

        # Log only API requests to avoid logging admin/static file requests
        if request.path.startswith('/api/'):
            try:
                user = request.user if request.user.is_authenticated else None

                # Get client IP address
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[0]
                else:
                    ip_address = request.META.get('REMOTE_ADDR')

                OperationLog.objects.create(
                    user=user,
                    operation=f"{request.method} {request.path}",
                    ip_address=ip_address,
                    is_success=(200 <= response.status_code < 300),
                    details={
                        "request_body": request.POST.dict() if request.POST else {},
                        "response_status": response.status_code,
                        "duration_ms": round(duration * 1000, 2)
                    }
                )
            except Exception as e:
                logger.error(f"Failed to create operation log: {e}")

        return response
