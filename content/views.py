from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from .models import Content, Rating
from .serializers import ContentListSerializer, RatingSerializer
from .throttling import UserRateThrottle, IPRateThrottle, SuspiciousActivityThrottle
from .utils import check_suspicious_activity, validate_account_age, get_client_ip
from django.shortcuts import render
from django.http import JsonResponse



class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentListSerializer
    throttle_classes = [IPRateThrottle]

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True,
            methods=['POST'],
            permission_classes=[IsAuthenticated],
            throttle_classes=[UserRateThrottle, SuspiciousActivityThrottle])
    def rate(self, request, pk=None):
        """Rate a content item with anti-manipulation checks"""
        content = self.get_object()
        user = request.user

        # Check account age
        if not validate_account_age(user):
            return Response(
                {"error": "Account too new to rate"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get and store IP address
        ip_address = get_client_ip(request)

        # Check for suspicious activity
        if check_suspicious_activity(user, ip_address):
            return Response(
                {"error": "Rating limited due to suspicious activity"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            score = serializer.validated_data['score']

            # Check if rating is an outlier
            if content.is_rating_outlier(score):
                # Don't reject but flag as suspicious
                cache.set(f'suspicious_user_{user.pk}', True, timeout=3600)

            with transaction.atomic():
                rating, created = Rating.objects.update_or_create(
                    user=user,
                    content=content,
                    defaults={
                        'score': score,
                        'ip_address': ip_address
                    }
                )

                # Update cached statistics
                content.update_rating_stats()

                # Invalidate cached weighted average
                cache.delete(f'weighted_avg_{content.id}')

            return Response({
                'status': 'success',
                'message': 'Rating updated' if not created else 'Rating created'
            })

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

def home(request):
    return render(request, 'index.html')


def content_list(request):
    contents = Content.objects.all()
    data = []
    for content in contents:
        data.append({
            'id': content.id,
            'title': content.title,
            'text': content.text,
            'rating_average': content.rating_average,
            'rating_count': content.rating_count,
        })
    return JsonResponse(data, safe=False)


def rate_content(request, content_id):
    if request.method == 'POST':
        try:
            content = Content.objects.get(id=content_id)
            score = int(request.POST.get('score'))  # Ensure you get the rating score
            # Update the rating logic (this is just an example)
            content.rating_count += 1
            content.rating_average = (content.rating_average * (
                        content.rating_count - 1) + score) / content.rating_count
            content.save()

            return JsonResponse({'message': 'Rating updated successfully', 'rating_average': content.rating_average,
                                 'rating_count': content.rating_count})

        except Content.DoesNotExist:
            return JsonResponse({'error': 'Content not found'}, status=404)

        except ValueError:
            return JsonResponse({'error': 'Invalid rating value'}, status=400)