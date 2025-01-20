from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class UserListView(generics.ListCreateAPIView):
    """
    get:
    Return a list of all users (admin only).

    post:
    Create a new user (admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the details of a specific user.

    put:
    Update a user's information.

    delete:
    Delete a user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()

class RegisterView(generics.CreateAPIView):
    """
    Register a new user and return authentication tokens.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "testuser",
                            "email": "test@example.com",
                            "first_name": "Test",
                            "last_name": "User"
                        },
                        "tokens": {
                            "access": "eyJ0...",
                            "refresh": "eyJ0..."
                        },
                        "message": "User registered successfully"
                    }
                }
            )
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': serializer.data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'message': 'User registered successfully. Use these tokens for authentication.',
            'usage': 'Include the access token in the Authorization header like this: Bearer <access_token>'
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Get JWT token pair",
        responses={
            200: openapi.Response(
                description="Token pair obtained successfully",
                examples={
                    "application/json": {
                        "access": "eyJ0...",
                        "refresh": "eyJ0...",
                        "usage": "Include the access token in the Authorization header"
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.data['usage'] = 'Include the access token in the Authorization header like this: Bearer <access_token>'
        return response
