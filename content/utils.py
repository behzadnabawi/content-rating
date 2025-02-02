from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import Rating


def check_suspicious_activity(user, ip_address):
    """Check for suspicious rating patterns"""
    recent_ratings = Rating.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(minutes=5)
    ).count()

    ip_ratings = Rating.objects.filter(
        ip_address=ip_address,
        created_at__gte=timezone.now() - timedelta(minutes=5)
    ).count()

    # Flag suspicious activity
    if recent_ratings > 10 or ip_ratings > 20:
        cache.set(f'suspicious_user_{user.pk}', True, timeout=86400)  # 24 hours
        return True
    return False


def validate_account_age(user):
    """Check if account is too new"""
    account_age = timezone.now() - user.date_joined
    return account_age >= timedelta(days=1)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')