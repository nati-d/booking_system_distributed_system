import json
import os
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken

from django.contrib.auth import get_user_model
from .serializers import UserSerializer, LoginSerializer, UserProfileSerializer, PublicUserSerializer
import pika 
User = get_user_model() 


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
class ValidateTokenView(APIView):
    """
    API View to validate a JWT token and return user data if valid.
    """
    # permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        print(token,11)
        print(token)
        if not token:
            return Response({"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the token to validate it
            access_token = AccessToken(token)
            
            # Check if token is valid and not expired
            user_id = access_token.get("user_id")
            if not user_id:
                print(1111)
                return Response({"error": "Invalid token payload."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Optionally check for blacklisted token
            # if hasattr(access_token, "check_blacklist") and access_token.check_blacklist():
            #     return Response({"error": "Token has been blacklisted."}, status=status.HTTP_401_UNAUTHORIZED)

            # Retrieve the user from the database
            user = User.objects.get(id=user_id)
            
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            return Response({"valid": True, "user": user_data}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"valid": False, "error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Generic error handling for debugging
            return Response({"valid": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteUserView(APIView): 
    """
    API View to delete a user and notify the booking service.
    """
    def delete(self, request, user_id):
        try:
            # Fetch the user
            user = User.objects.get(id=user_id)

            # Delete the user
            user.delete()
 
            # Publish to RabbitMQ queue
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials
            ))
            channel = connection.channel()

            # Declare the queue
            channel.queue_declare(queue='delete_user')

            # Publish the message with user ID
            message = {"user_id": user_id}
            channel.basic_publish(
                exchange='',
                routing_key='delete_user',
                body=json.dumps(message)
            )

            print(f"[x] Sent delete notification: {message}")

            # Close the connection
            connection.close()

            return Response({"message": f"User {user_id} deleted successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except pika.exceptions.AMQPConnectionError as e:
            return Response({"error": f"Failed to connect to RabbitMQ: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserListView(generics.ListCreateAPIView): 
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        response_data = serializer.data
        response_data.pop('password', None)
        response_data.pop('password2', None)
        response_data['message'] = 'User updated successfully'
        
        return Response(response_data)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        response_data = serializer.data
        response_data.pop('password', None)
        response_data.pop('password2', None)
        response_data['message'] = 'User registered successfully'
        
        response = Response(response_data, status=status.HTTP_201_CREATED)
        response.set_cookie(
            'refresh_token',
            str(refresh),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=24 * 60 * 60
        )
        
        return response

class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        response_data = {
            'email': validated_data['email'],
            'access': validated_data['access'],
            'message': 'Login successful'
        }
        
        response = Response(response_data)
        
        response.set_cookie(
            'refresh_token',
            validated_data['refresh'],
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=24 * 60 * 60
        )
        
        return response

class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            response = Response({'message': 'Successfully logged out'})
            response.delete_cookie('refresh_token')
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=24 * 60 * 60
            )
            
            response.data = {
                'access_token': access_token,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email
                },
                'message': 'Login successful',
                'usage': 'Include the access token in the Authorization header like this: Bearer <access_token>'
            }
        
        return response

class UserSearchView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PublicUserSerializer

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {"detail": "Email parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"detail": "No user found with this email"},
                status=status.HTTP_404_NOT_FOUND
            )

class TokenRefreshViewWithCookie(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            refresh_token = response.data.get('refresh')
            
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=24 * 60 * 60
            )
        
        return response

class UserDetailByIdView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PublicUserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
