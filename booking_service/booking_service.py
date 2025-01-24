import os
import json
import pika
import time
import requests


# Consumer
def delete_user_consumer():
    print('Starting consumer...')

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

    # Retry mechanism for RabbitMQ connection 
    max_retries = 5
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials
            ))
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            time.sleep(5)
    else:
        print("Failed to connect to RabbitMQ after several attempts.")
        return

    channel = connection.channel()

    # Declare queue with durability settings
    channel.queue_declare(queue='delete_user', durable=True)


    def callback(ch, method, properties, body):
        message = json.loads(body)
        user_id = message.get('user_id')
        if user_id:
            try:
                response = requests.post('http://localhost:8000/delete_user_events/', json={'user_id': user_id})
                if response.status_code == 200:
                    print(f"Successfully deleted events for user_id {user_id}.")
                else:
                    print(f"Failed to delete events for user_id {user_id}. Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"HTTP request failed: {e}")
    channel.basic_consume(queue='delete_user', on_message_callback=callback, auto_ack=True) 
 
    print(' [*] Waiting for messages. To exit press CTRL+C') 
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Consumer interrupted, closing cxonnections.")
    finally:
        # Close RabbitMQ connection gracefully
        connection.close()

if __name__ == "__main__":
    delete_user_consumer()
