from rest_framework import serializers
from django.contrib.auth import get_user_model
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
                 'first_name', 'last_name')
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
            last_name=validated_data.get('last_name', '')
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

class PublicUserSerializer(serializers.ModelSerializer):
    """
    Serializer for public user information (used when viewing other users)
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name']
        read_only_fields = fields  # All fields are read-only

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile operations (view/update)
    """
    email = serializers.EmailField(read_only=True)  # Email can't be changed directly
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 
                 'current_password', 'new_password', 
                 'confirm_new_password']
        read_only_fields = ['id', 'email']

    def validate(self, data):
        # If any password field is provided, all password fields must be provided
        password_fields = ['current_password', 'new_password', 'confirm_new_password']
        if any(field in data for field in password_fields):
            for field in password_fields:
                if field not in data:
                    raise serializers.ValidationError(
                        f"{field} is required when changing password"
                    )
            
            # Verify current password
            if not self.instance.check_password(data['current_password']):
                raise serializers.ValidationError(
                    {"current_password": "Current password is incorrect"}
                )
            
            # Validate new password
            if data['new_password'] != data['confirm_new_password']:
                raise serializers.ValidationError(
                    {"confirm_new_password": "New passwords don't match"}
                )
            
            try:
                validate_password(data['new_password'])
            except ValidationError as e:
                raise serializers.ValidationError({"new_password": list(e)})

        return data

    def update(self, instance, validated_data):
        # Remove password fields from validated_data
        validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('confirm_new_password', None)

        # Update password if provided
        if new_password:
            instance.set_password(new_password)

        # Update other fields
        return super().update(instance, validated_data)

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
