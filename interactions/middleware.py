import json
import time

from django.utils.deprecation import MiddlewareMixin

from .models import APIInteraction


class APIInteractionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Store start time for response time calculation
        request._start_time = time.time()

        # Store original request body for later use
        try:
            if hasattr(request, "body") and request.body:
                request._body = request.body.decode("utf-8")
            else:
                request._body = None
        except (UnicodeDecodeError, AttributeError):
            request._body = None

        return None

    def process_response(self, request, response):
        # Only track API requests (you can customize this filter)
        if not request.path.startswith("/api/"):
            return response

        try:
            # Calculate response time
            response_time_ms = None
            if hasattr(request, "_start_time"):
                response_time_ms = int((time.time() - request._start_time) * 1000)

            # Get client IP address
            ip_address = self.get_client_ip(request)

            # Parse request headers
            headers = {}
            for key, value in request.META.items():
                if key.startswith("HTTP_"):
                    # Convert HTTP_HEADER_NAME to Header-Name format
                    header_name = key[5:].replace("_", "-").title()
                    headers[header_name] = value

            # Parse query parameters
            query_params = dict(request.GET.items())

            # Parse request body
            request_body = None
            if hasattr(request, "_body") and request._body:
                try:
                    request_body = json.loads(request._body)
                except (json.JSONDecodeError, TypeError):
                    # If not JSON, store as string
                    request_body = request._body

            # Parse response body
            response_body = None
            try:
                if hasattr(response, "content") and response.content:
                    content = response.content.decode("utf-8")
                    if response.get("Content-Type", "").startswith("application/json"):
                        response_body = json.loads(content)
                    else:
                        response_body = content
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                pass

            # Create interaction record
            APIInteraction.objects.create(
                method=request.method,
                path=request.path,
                full_url=request.build_absolute_uri(),
                query_params=query_params,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                ip_address=ip_address,
                headers=headers,
                request_body=request_body,
                content_type=request.content_type,
                status_code=response.status_code,
                response_body=response_body,
                response_time_ms=response_time_ms,
                user=request.user
                if hasattr(request, "user") and request.user.is_authenticated
                else None,
            )

        except Exception as e:
            # Log the error but don't break the request/response cycle
            print(f"Error saving API interaction: {e}")

        return response

    def get_client_ip(self, request):
        """Extract the client's IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
