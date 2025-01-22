from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('initialize/', views.initialize_payment, name='initialize_payment'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('success/', views.success, name='payment_success'),
    path('cancel/', views.cancel, name='payment_cancel'),
    
    # Template view (if needed)
    path('payment-form/', views.initialize_payment_legacy, name='payment_form'),
]
