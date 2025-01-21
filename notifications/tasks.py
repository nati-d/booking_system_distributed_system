from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

@shared_task
def send_notification_email(notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        subject = f"Notification for Ticket: {notification.ticket.title}"
        message = notification.message
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [notification.user.email]
        
        send_mail(subject, message, from_email, recipient_list)
        return f"Email sent successfully to {notification.user.email}"
    except Notification.DoesNotExist:
        return "Notification not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"

