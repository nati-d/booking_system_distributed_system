from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .chapa_service import ChapaService

@api_view(['POST'])
def initialize_payment(request):
    """Initialize a payment transaction"""
    try:
        amount = request.data.get('amount')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        
        if not all([amount, email, first_name, last_name]):
            return Response({
                'error': 'Missing required fields. Please provide amount, email, first_name, and last_name'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment payload
        payload = {
            'amount': amount,
            'currency': 'ETB',
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'tx_ref': f'tx-{email}-{amount}',  # You might want to generate a unique reference
            'callback_url': f'{settings.PAYMENT_SERVICE_PUBLIC_URL}/payments/verify/',
            'return_url': f'{settings.PAYMENT_SERVICE_PUBLIC_URL}/payments/success/'
        }
        
        # Initialize payment with Chapa
        response = ChapaService.initialize_payment(payload)
        return Response(response, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def verify_payment(request):
    """Verify a payment transaction"""
    try:
        tx_ref = request.query_params.get('tx_ref')
        if not tx_ref:
            return Response({
                'error': 'Transaction reference is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify payment with Chapa
        response = ChapaService.verify_payment(tx_ref)
        return Response(response, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def success(request):
    """Handle successful payment"""
    try:
        tx_ref = request.query_params.get('tx_ref')
        status_code = request.query_params.get('status')
        
        # You might want to verify the payment here as well
        return Response({
            'message': 'Payment successful',
            'tx_ref': tx_ref,
            'status': status_code
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def cancel(request):
    """Handle cancelled payment"""
    return Response({
        'message': 'Payment was cancelled'
    }, status=status.HTTP_200_OK)

def initialize_payment_legacy(request):
    if request.method == "POST":
        payload = {
            "amount": request.POST.get("amount", "10"),
            "currency": "ETB",
            "email": request.POST.get("email"),
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "phone_number": request.POST.get("phone_number"),
            "tx_ref": "unique_transaction_ref_12345",  # Generate unique transaction reference
            "callback_url": f'{settings.PAYMENT_SERVICE_PUBLIC_URL}/payments/callback/',
            "return_url": f'{settings.PAYMENT_SERVICE_PUBLIC_URL}/payments/success/',
            "customization": {
                "title": "Payment for my service",
                "description": "Testing Chapa Integration"
            }
        }
        response = ChapaService.initialize_payment(payload)
        return JsonResponse(response)
    return render(request, "payments/initialize_payment.html")
