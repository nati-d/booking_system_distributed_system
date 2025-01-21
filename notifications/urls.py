from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

