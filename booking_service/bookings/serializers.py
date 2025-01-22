from rest_framework import serializers
from .models import Event, Booking, Payment

# Event Serializer
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'date', 'time', 'location', 
            'total_tickets', 'available_tickets', 'price_per_ticket'
        ]

# Booking Serializer
class BookingSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user_id', 'event', 'tickets_booked', 'status', 'event_name']

    def validate(self, attrs):
        # Custom validation to ensure there are enough available tickets
        event = attrs.get('event')
        tickets_booked = attrs.get('tickets_booked')
        
        if event and tickets_booked > event.available_tickets:
            raise serializers.ValidationError("Not enough tickets available.")
        
        return attrs

    def create(self, validated_data):
        # Deduct tickets from the event before saving the booking
        event = validated_data.get('event')
        tickets_booked = validated_data.get('tickets_booked')

        # Ensure the event has enough tickets available
        if event.available_tickets < tickets_booked:
            raise serializers.ValidationError("Not enough tickets available.")
        
        # Deduct the tickets from the event and save the booking
        event.available_tickets -= tickets_booked
        event.save()

        return super().create(validated_data)

# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    booking_user = serializers.CharField(source='booking.user_id', read_only=True)
    booking_event = serializers.CharField(source='booking.event.name', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_date', 'status', 'booking_user', 'booking_event']

    def validate(self, attrs):
        # Validate payment only if the booking status is pending
        booking = attrs.get('booking')
        if booking and booking.status != 'pending':
            raise serializers.ValidationError("Payment can only be made for pending bookings.")
        return attrs

    def create(self, validated_data):
        # After payment, update booking status to 'confirmed'
        booking = validated_data.get('booking')
        booking.status = 'confirmed'
        booking.save()

        return super().create(validated_data)
