from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import apiviews

router = DefaultRouter()
router.register(r'products', apiviews.ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]