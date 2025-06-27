from django.db import models
from django.core.validators import EmailValidator, RegexValidator
import os
import uuid
import secrets
import hashlib


def user_profile_picture_path(instance, filename):
    """Generate file path for user profile pictures"""
    # Use UUID if instance doesn't have an ID yet (during creation)
    identifier = instance.id if instance.id else str(uuid.uuid4())
    return f'profile_pictures/{identifier}/{filename}'


class APIKey(models.Model):
    """API Key model for authentication without traditional login"""
    key_name = models.CharField(
        max_length=100,
        help_text="Descriptive name for this API key"
    )
    key_prefix = models.CharField(
        max_length=8,
        unique=True,
        help_text="Public prefix of the API key"
    )
    key_hash = models.CharField(
        max_length=128,
        help_text="Hashed version of the complete API key"
    )
    permissions = models.JSONField(
        default=dict,
        help_text="Permissions for this API key"
    )
    is_active = models.BooleanField(default=True)
    rate_limit = models.PositiveIntegerField(
        default=1000,
        help_text="Requests per hour limit"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def __str__(self):
        return f"{self.key_name} ({self.key_prefix}...)"

    @classmethod
    def generate_key(cls, name, permissions=None, rate_limit=1000):
        """Generate a new API key"""
        if permissions is None:
            permissions = {'users': ['read', 'write']}
        
        # Generate a secure random key
        key = secrets.token_urlsafe(32)
        prefix = key[:8]
        
        # Hash the complete key for storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        api_key = cls.objects.create(
            key_name=name,
            key_prefix=prefix,
            key_hash=key_hash,
            permissions=permissions,
            rate_limit=rate_limit
        )
        
        # Return the complete key (only time it's available in plain text)
        return api_key, key

    def verify_key(self, provided_key):
        """Verify if the provided key matches this API key"""
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        return self.key_hash == provided_hash

    def has_permission(self, resource, action):
        """Check if this API key has permission for a specific action on a resource"""
        if not self.is_active:
            return False
        
        resource_perms = self.permissions.get(resource, [])
        return action in resource_perms or 'admin' in resource_perms


class User(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="User's full name"
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Valid email address"
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Optional phone number"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Optional address"
    )
    age = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Optional age"
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        help_text="Optional profile picture"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.name} ({self.email})"

    def delete(self, *args, **kwargs):
        """Override delete to remove profile picture file"""
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)
