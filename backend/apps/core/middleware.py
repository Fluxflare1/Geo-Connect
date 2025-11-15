import uuid

from django.utils.deprecation import MiddlewareMixin


class RequestIdMiddleware(MiddlewareMixin):
    """
    Attaches a unique request_id to each request and response header X-Request-ID.
    """

    def process_request(self, request):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.request_id = rid

    def process_response(self, request, response):
        rid = getattr(request, "request_id", None)
        if rid:
            response["X-Request-ID"] = rid
        return response
