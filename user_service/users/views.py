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

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get the tokens from the response
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            
            # Set HTTP-only cookie for refresh token
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=True,  # Use only with HTTPS
                samesite='Lax',
                max_age=24 * 60 * 60  # 1 day
            )
            
            # Return a structured response
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

class LogoutView(APIView):
    """
    Logout view to clear the refresh token cookie
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Clear the refresh token cookie
            response = Response({'message': 'Successfully logged out'})
            response.delete_cookie('refresh_token')
            
            # Blacklist the refresh token if you're using token blacklist feature
            try:
                refresh_token = request.COOKIES.get('refresh_token')
                if refresh_token:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
            except Exception:
                pass
                
            return response
            
        except Exception as e:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
