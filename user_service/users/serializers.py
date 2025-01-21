from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 
                 'first_name', 'last_name', 'is_event_organizer')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate_password(self, value):
        """
        Validate password strength
        """
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Additional password validation
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # Remove password2 from the data
        
        # Create user with hashed password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],  # password will be hashed by create_user
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_event_organizer=validated_data.get('is_event_organizer', False)
        )
        return user

    def update(self, instance, validated_data):
        # Handle password update separately
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)
        
        if password and password2:
            if password != password2:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
            instance.set_password(password)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError('An email address is required to login.')

        if password is None:
            raise serializers.ValidationError('A password is required to login.')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('No account found with this email address.')

        if not user.check_password(password):
            raise serializers.ValidationError('Invalid password.')

        if not user.is_active:
            raise serializers.ValidationError('This user has been deactivated.')

        refresh = RefreshToken.for_user(user)

        return {
            'email': user.email,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }