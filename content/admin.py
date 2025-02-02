# First, register your model in content/admin.py:
from django.contrib import admin
from .models import Content, Rating

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating_average', 'rating_count')
    search_fields = ('title', 'text')
