from django.urls import path
from . import views

urlpatterns = [
    path('select/<uuid:order_number>/', views.payment_select, name='payment_select'),
    path('initiate/<uuid:order_number>/', views.initiate_payment, name='initiate_payment'),
    path('esewa/<uuid:payment_id>/', views.esewa_redirect, name='esewa_redirect'),
    path('khalti/<uuid:payment_id>/', views.khalti_redirect, name='khalti_redirect'),
    path('esewa/success/', views.esewa_success, name='esewa_success'),
    path('success/<uuid:payment_id>/', views.payment_success, name='payment_success'),
]