from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.db import models

# Create your models here.

class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser
    """
    email = models.EmailField(unique=True)
    is_event_organizer = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Email & password are required by default
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        """
        Override set_password to ensure password hashing
        """
        self.password = make_password(raw_password)
        self._password = raw_password
        
    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password matches the password
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
            
        return check_password(raw_password, self.password, setter)