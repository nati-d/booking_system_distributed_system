from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, LoginSerializer, UserProfileSerializer, PublicUserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class UserListView(generics.ListCreateAPIView):
    """r
    get:
    Return a list of all users (admin only).

    post:
    Create a new user (admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user information.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()

    @swagger_auto_schema(
        operation_description="Get user details",
        responses={
            200: openapi.Response(
                description="User details retrieved successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_event_organizer": False
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication failed",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="""
        Update user information. Fields that can be updated:
        - First name
        - Last name
        - Email (must be unique)
        - Password (must meet strength requirements)
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description='New email address',
                    example='new.email@example.com'
                ),
                'first_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New first name',
                    example='John'
                ),
                'last_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New last name',
                    example='Doe'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New password (must meet strength requirements)',
                    example='NewSecurePass123!'
                ),
                'password2': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New password confirmation',
                    example='NewSecurePass123!'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="User updated successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "new.email@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_event_organizer": False,
                        "message": "User updated successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "email": [
                            "This email is already in use."
                        ],
                        "password": [
                            "Password must be at least 8 characters long.",
                            "Password must contain at least one uppercase letter.",
                            "Password must contain at least one number.",
                            "Password must contain at least one special character."
                        ],
                        "password2": [
                            "Password fields didn't match."
                        ]
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication failed",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            )
        }
    )
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

    @swagger_auto_schema(
        operation_description="Partially update user information",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description='New email address'
                ),
                'first_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New first name'
                ),
                'last_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New last name'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New password'
                ),
                'password2': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New password confirmation'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="User partially updated successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_event_organizer": False,
                        "message": "User updated successfully"
                    }
                }
            )
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_description="Get current user's profile",
        responses={
            200: openapi.Response(
                description="Profile retrieved successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "email": "john@example.com",
                        "username": "john_doe",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_event_organizer": False
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication failed",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="""
        Update user profile. You can update:
        - Username
        - First name
        - Last name
        - Password (requires current_password, new_password, and confirm_new_password)
        
        Note: Email cannot be changed directly for security reasons.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New username'
                ),
                'first_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New first name'
                ),
                'last_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New last name'
                ),
                'current_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Current password (required for password change)'
                ),
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New password (must meet password requirements)'
                ),
                'confirm_new_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Confirm new password'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "email": "john@example.com",
                        "username": "john_doe",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_event_organizer": False
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "username": [
                            "This username is already taken."
                        ],
                        "current_password": [
                            "Current password is incorrect"
                        ],
                        "new_password": [
                            "Password must be at least 8 characters long.",
                            "Password must contain at least one uppercase letter.",
                            "Password must contain at least one number.",
                            "Password must contain at least one special character."
                        ],
                        "confirm_new_password": [
                            "New passwords don't match"
                        ]
                    }
                }
            )
        }
    )
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    """
    Register a new user with email and password.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="""
        Register a new user with the following requirements:
        - Username must be unique
        - Email must be unique and valid
        - Password must be at least 8 characters long and contain:
          * At least one uppercase letter
          * At least one lowercase letter
          * At least one number
          * At least one special character (!@#$%^&*(),.?":{}|<>)
        - Password confirmation (password2) must match password
        - First name and last name are required
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password', 'password2', 'first_name', 'last_name'],
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Unique username',
                    example='john_doe'
                ),
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description='Unique email address',
                    example='john@example.com'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Strong password (min 8 chars, must include uppercase, lowercase, number, and special char)',
                    example='SecurePass123!'
                ),
                'password2': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Password confirmation',
                    example='SecurePass123!'
                ),
                'first_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User\'s first name',
                    example='John'
                ),
                'last_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User\'s last name',
                    example='Doe'
                ),
                'is_event_organizer': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Whether the user is an event organizer',
                    default=False,
                    example=False
                ),
            }
        ),
        responses={
            201: openapi.Response(
                description="User successfully registered",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_event_organizer": False,
                        "message": "User registered successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "username": [
                            "A user with that username already exists."
                        ],
                        "email": [
                            "This field must be unique."
                        ],
                        "password": [
                            "Password must be at least 8 characters long.",
                            "Password must contain at least one uppercase letter.",
                            "Password must contain at least one number.",
                            "Password must contain at least one special character."
                        ],
                        "password2": [
                            "Password fields didn't match."
                        ]
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
        
        response_data = serializer.data
        response_data.pop('password', None)
        response_data.pop('password2', None)
        response_data['message'] = 'User registered successfully'
        
        # Set refresh token in HTTP-only cookie
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
    """
    Login user with email and password, returns JWT tokens
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description="""
        Login with email and password to receive JWT tokens.
        The access token should be included in the Authorization header for protected endpoints.
        The refresh token is stored in an HTTP-only cookie.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description='Email address',
                    example='john@example.com'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Password',
                    example='SecurePass123!'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "email": "john@example.com",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "message": "Login successful"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "non_field_errors": [
                            "No account found with this email address.",
                            "Invalid password."
                        ]
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the validated data
        validated_data = serializer.validated_data
        
        response_data = {
            'email': validated_data['email'],
            'access': validated_data['access'],
            'message': 'Login successful'
        }
        
        # Create the response
        response = Response(response_data)
        
        # Set the refresh token in an HTTP-only cookie
        response.set_cookie(
            'refresh_token',
            validated_data['refresh'],
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=24 * 60 * 60  # 1 day
        )
        
        return response

class LogoutView(generics.GenericAPIView):
    """
    Logout user and blacklist the refresh token
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout user and invalidate refresh token",
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "message": "Successfully logged out"
                    }
                }
            )
        }
    )
    def post(self, request):
        try:
            # Get the refresh token from cookie
            refresh_token = request.COOKIES.get('refresh_token')
            
            if refresh_token:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Create response and delete the refresh token cookie
            response = Response({'message': 'Successfully logged out'})
            response.delete_cookie('refresh_token')
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

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
                secure=True,
                samesite='Lax',
                max_age=24 * 60 * 60
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

class UserSearchView(generics.GenericAPIView):
    """
    Search for users by email
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PublicUserSerializer

    @swagger_auto_schema(
        operation_description="Search for a user by email",
        manual_parameters=[
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                description="Email to search for",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="User found",
                examples={
                    "application/json": {
                        "id": 1,
                        "email": "john@example.com",
                        "username": "john_doe",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_event_organizer": False
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                        "detail": "No user found with this email"
                    }
                }
            )
        }
    )
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

class UserDetailByIdView(generics.RetrieveAPIView):
    """
    Retrieve user details by ID
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PublicUserSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(
        operation_description="Get user details by ID",
        responses={
            200: openapi.Response(
                description="User details retrieved successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "email": "john@example.com",
                        "username": "john_doe",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_event_organizer": False
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                        "detail": "Not found."
                    }
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
