from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('order-created/<uuid:order_number>/', views.order_created, name='order_created'),
    path('orders/', views.order_list, name='order_list'),
    path('order/<uuid:order_number>/', views.order_detail, name='order_detail'),
]