from django.urls import path, include

from .views import customer_get_restaurant

urlpatterns = [
  path('restaurants/', customer_get_restaurant),
]