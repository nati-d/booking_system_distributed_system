from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/create/', views.EventCreateView.as_view(), name='create_event'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='create_booking'),
    path('payments/', views.PaymentView.as_view(), name='make_payment'),
]
