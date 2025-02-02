from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'content', views.ContentViewSet)


urlpatterns = [
    # path('', include(router.urls)),
    path('', views.home, name='home'),
    path('content/', views.content_list, name='content_list'),
    path('content/<int:content_id>/rate/', views.rate_content, name='rate_content'),

]