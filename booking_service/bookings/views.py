import requests
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Event, Booking, Payment
from .serializers import EventSerializer, BookingSerializer, PaymentSerializer
from django.db.models import F
from rest_framework.exceptions import AuthenticationFailed
from .permissions import IsAuthenticatedWithToken  # Import the custom permission class
import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

def book_event(user_id, event_id, date):    
    """
    Simulate booking an event and sending a notification. 
    """
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        ))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue='booking_notifications')

        # Create the message
        message = {
            "user_id": user_id,
            "event_id": event_id,
            "date": date.isoformat()  # Convert date to ISO format string
        }

        # Publish the message
        channel.basic_publish(
            exchange='',
            routing_key='booking_notifications',
            body=json.dumps(message)
        )

        print(f"[x] Sent booking notification: {message}")

        # Close the connection
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        raise

class EventListView(generics.ListAPIView):
    queryset = Event.objects.filter(available_tickets__gt=0).order_by('date')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedWithToken]

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedWithToken]

class EventCreateView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedWithToken]

class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedWithToken]

    def perform_create(self, serializer):  
        # Extract token from the Authorization header
        token = self.request.headers.get("Authorization").split(" ")[1]
        
        is_valid, user_data = self.validate_jwt_token(token)
        print(is_valid, user_data)
        if not is_valid:
            raise AuthenticationFailed("Authentication failed.")

        # Extract user ID from the validated token
        user_id = user_data.get("id")  # Ensure the response contains "id"

        event = serializer.validated_data['event']
        tickets_booked = serializer.validated_data['tickets_booked']

        book_event(user_id=user_id, event_id=event.id, date=event.date)

        # Check ticket availability
        if event.available_tickets < tickets_booked:
            raise ValueError("Not enough tickets available.")

        # Deduct tickets and save the event
        event.available_tickets = event.available_tickets - tickets_booked
        event.save()

        # Save booking with the user ID
        serializer.save(user_id=user_id)

    def validate_jwt_token(self, token): 
        user_service_url = "http://127.0.0.1:8001/validate_token/"
        response = requests.post(user_service_url, json={"token": token})
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                return True, data
            else:
                return False, None
        else:
            return False, None

class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedWithToken]

    def get_queryset(self):
        # Extract token from the Authorization header
        token = self.request.headers.get("Authorization").split(" ")[1]
        is_valid, user_data = self.validate_jwt_token(token)

        if not is_valid:
            raise AuthenticationFailed("Authentication failed.")

        # Extract user ID from the validated token
        user_id = user_data.get("id")

        return Booking.objects.filter(user_id=user_id)

    def validate_jwt_token(self, token):
        user_service_url = "http://127.0.0.1:8001/validate_token/"
        response = requests.post(user_service_url, json={"token": token})
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                return True, data
            else:
                return False, None
        else:
            return False, None

class PaymentView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticatedWithToken]

    def perform_create(self, serializer):
        # Extract token from the Authorization header
        token = self.request.headers.get("Authorization").split(" ")[1]
        is_valid, user_data = self.validate_jwt_token(token)

        if not is_valid or not user_data:
            raise AuthenticationFailed("Authentication failed.")

        # Extract user ID from the validated token
        user_id = user_data.get("id")

        booking = serializer.validated_data['booking']
        if booking.status != 'pending':
            raise ValueError("Payment can only be made for pending bookings.")
        
        # Update booking status and save
        booking.status = 'confirmed'
        booking.save()
        serializer.save()

    def validate_jwt_token(self, token):
        user_service_url = "http://127.0.0.1:8001/validate_token/"
        response = requests.post(user_service_url, json={"token": token})
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                return True, data
            else:
                return False, None
        else:
            return False, None