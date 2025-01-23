import os
import json
import pika
from django.conf import settings
from bookings.models import Booking  # Import the Booking model
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "booking_service.settings")

from django.conf import settings

print(111111,'yes')

# Consumer
def delete_user_consumer():
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.queue_declare(queue='delete_user')

    def callback(ch, method, properties, body):
        message = json.loads(body)
        user_id = message.get("user_id")
        if user_id:
            Booking.objects.filter(user_id=user_id).delete()
            print(f"[x] Deleted bookings for user_id: {user_id}")

    channel.basic_consume(queue='delete_user', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    delete_user_consumer()