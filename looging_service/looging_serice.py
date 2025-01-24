import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

def send_notification(message):
    """
    Simulate sending a notification to the user.
    """
    data = json.loads(message)
    print(f"Notification: User {data['user_id']} booked event {data['event_id']} on {data['date']}")

def callback(ch, method, properties, body):
    """
    Callback function to handle messages from the queue.
    """
    print("[x] Received message")
    send_notification(body)

def main():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue='booking_notifications')

    # Start consuming messages
    print("[*] Waiting for messages. To exit, press CTRL+C")
    channel.basic_consume(queue='booking_notifications', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

if __name__ == "__main__":
    main()
