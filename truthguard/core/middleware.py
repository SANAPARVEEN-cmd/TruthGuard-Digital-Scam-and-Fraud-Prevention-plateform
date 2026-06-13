import time
from collections import defaultdict

from django.http import HttpResponseForbidden


class RateLimitMiddleware:
    """Simple IP-based rate limiting for form submissions and search."""

    RATE_LIMITS = {
        '/search/': (30, 60),
        '/report/': (10, 60),
        '/accounts/login/': (20, 60),
        '/accounts/register/': (10, 60),
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self._requests = defaultdict(list)

    def __call__(self, request):
        if request.method == 'POST':
            path = request.path
            for route, (limit, window) in self.RATE_LIMITS.items():
                if path.startswith(route) or path == route:
                    ip = self._get_client_ip(request)
                    key = f'{ip}:{route}'
                    now = time.time()
                    self._requests[key] = [
                        t for t in self._requests[key] if now - t < window
                    ]
                    if len(self._requests[key]) >= limit:
                        return HttpResponseForbidden(
                            'Rate limit exceeded. Please try again later.'
                        )
                    self._requests[key].append(now)
                    break

        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
