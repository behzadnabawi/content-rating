from rest_framework import serializers
from .models import Content, Rating


class ContentListSerializer(serializers.ModelSerializer):
    rating_count = serializers.IntegerField(read_only=True)
    rating_average = serializers.FloatField(read_only=True)
    user_rating = serializers.SerializerMethodField()
    weighted_average = serializers.SerializerMethodField()
    unique_raters_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Content
        fields = ['id', 'title', 'rating_count', 'rating_average',
                  'user_rating', 'weighted_average', 'unique_raters_count']

    def get_user_rating(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                rating = Rating.objects.get(user=user, content=obj)
                return rating.score
            except Rating.DoesNotExist:
                return None
        return None

    def get_weighted_average(self, obj):
        return obj.get_weighted_average()



class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']

    def validate_score(self, value):
        if not (0 <= value <= 5):
            raise serializers.ValidationError("Score must be between 0 and 5")
        return value
