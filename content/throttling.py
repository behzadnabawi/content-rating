from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django.utils import timezone


class IPRateThrottle(AnonRateThrottle):
    rate = '50/hour'

    def get_cache_key(self, request, view):
        return f'ip_throttle_{self.get_ident(request)}'


class UserRateThrottle(UserRateThrottle):
    rate = '10/hour'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f'user_throttle_{request.user.pk}'
        return f'anon_throttle_{self.get_ident(request)}'


class SuspiciousActivityThrottle(UserRateThrottle):
    rate = '30/day'  # Stricter limit for suspicious users

    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return True

        # Check if user has been flagged as suspicious
        is_suspicious = cache.get(f'suspicious_user_{request.user.pk}')
        if is_suspicious:
            return super().allow_request(request, view)
        return True