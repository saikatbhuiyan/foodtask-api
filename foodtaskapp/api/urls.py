from django.urls import path, include

from . import views

urlpatterns = [

  path('restaurants/', views.customer_get_restaurants),
  path('meals/<restaurant_id>/', views.customer_get_meals),
  path('order/add/', views.customer_add_order),
  path('order/latest/', views.customer_get_latest_order),
  path('order/notification/<last_request_time>/', views.restaurant_order_notification),

]