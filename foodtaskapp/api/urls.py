from django.urls import path, include

from . import views

urlpatterns = [

  path('customer/restaurants/', views.customer_get_restaurants),
  path('customer/meals/<restaurant_id>/', views.customer_get_meals),
  path('customer/order/add/', views.customer_add_order),
  path('customer/order/latest/', views.customer_get_latest_order),

  path('restaurant/order/notification/<last_request_time>/', views.restaurant_order_notification),

  # APIs for DRIVERS
  path(r'^api/driver/orders/ready/', views.driver_get_ready_orders),
  path(r'^api/driver/order/pick/', views.driver_pick_order),
  path(r'^api/driver/order/latest/', views.driver_get_latest_order),
  path(r'^api/driver/order/complete/', views.driver_complete_order),
  path(r'^api/driver/revenue/', views.driver_get_revenue),

]