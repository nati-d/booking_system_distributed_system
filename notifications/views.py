from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ticket, Notification
from .serializers import TicketSerializer, NotificationSerializer
from .tasks import send_notification_email

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        ticket = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Ticket.STATUS_CHOICES):
            old_status = ticket.status
            ticket.status = new_status
            ticket.save()

            # Create notifications for user and admin
            user_notification = Notification.objects.create(
                ticket=ticket,
                user=ticket.created_by,
                message=f"Your ticket '{ticket.title}' status has changed from {old_status} to {new_status}."
            )
            admin_notification = Notification.objects.create(
                ticket=ticket,
                user=ticket.assigned_to or ticket.created_by,  # Assign to the assigned user or the creator if no one is assigned
                message=f"Ticket '{ticket.title}' status has changed from {old_status} to {new_status}."
            )

            # Send email notifications
            send_notification_email.delay(user_notification.id)
            send_notification_email.delay(admin_notification.id)

            return Response({'status': 'Ticket status updated'})
        return Response({'status': 'Invalid status'}, status=400)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'})

