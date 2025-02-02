from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, StdDev
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone
import statistics


class Content(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Cached fields for performance
    rating_count = models.PositiveIntegerField(default=0)
    rating_average = models.FloatField(default=0.0)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['rating_average']),
        ]

    def is_rating_outlier(self, score):
        """Check if a rating is statistically an outlier"""
        ratings = list(self.ratings.values_list('score', flat=True))
        if len(ratings) < 5:  # Need minimum ratings for statistical significance
            return False

        mean = statistics.mean(ratings)
        try:
            std_dev = statistics.stdev(ratings)
            return abs(score - mean) > 2 * std_dev
        except statistics.StatisticsError:
            return False

    def get_weighted_average(self):
        """Get time-weighted average rating to prevent manipulation"""
        cache_key = f'weighted_avg_{self.id}'
        cached_value = cache.get(cache_key)

        if cached_value is not None:
            return cached_value

        now = timezone.now()

        # Multiple time windows for more granular weighting
        windows = [
            (timedelta(hours=24), 0.3),  # Last 24 hours: 30% weight
            (timedelta(days=7), 0.5),  # Last week: 50% weight
            (None, 0.7)  # All time: 70% weight
        ]

        weighted_sum = 0
        total_weight = 0

        for time_delta, weight in windows:
            query = self.ratings.all()
            if time_delta:
                query = query.filter(created_at__gte=now - time_delta)

            avg = query.aggregate(Avg('score'))['score__avg'] or 0
            weighted_sum += avg * weight
            total_weight += weight

        weighted_avg = weighted_sum / total_weight if total_weight > 0 else 0
        cache.set(cache_key, weighted_avg, timeout=300)  # Cache for 5 minutes

        return weighted_avg

    def get_unique_raters_count(self):
        """Get the number of distinct users who have rated the content"""
        return self.ratings.values('user').distinct().count()


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True)
    is_suspicious = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'content']
        indexes = [
            models.Index(fields=['user', 'content']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
        ]