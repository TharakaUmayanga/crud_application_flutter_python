from django.db import models
from django.core.validators import EmailValidator, RegexValidator
import os
import uuid
import secrets
import hashlib


# Import validators for use in clean methods instead of field validators
def validate_name(value):
    from .validators import NameValidator
    validator = NameValidator()
    validator(value)

def validate_email(value):
    from .validators import CustomEmailValidator
    validator = CustomEmailValidator()
    validator(value)

def validate_phone(value):
    from .validators import PhoneNumberValidator
    validator = PhoneNumberValidator()
    validator(value)

def validate_address(value):
    from .validators import AddressValidator
    validator = AddressValidator()
    validator(value)

def validate_age(value):
    from .validators import AgeValidator
    validator = AgeValidator()
    validator(value)

def validate_image(value):
    from .validators import ImageValidator
    validator = ImageValidator()
    validator(value)

def validate_json_permissions(value):
    from .validators import JSONFieldValidator
    validator = JSONFieldValidator()
    validator(value)


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
        help_text="API key permissions (JSON format, max 10KB)"
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

    def clean(self):
        """Custom validation for API key"""
        super().clean()
        
        if self.permissions:
            validate_json_permissions(self.permissions)


class User(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="User's full name (letters, spaces, hyphens, apostrophes only)"
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        help_text="Valid email address"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="International phone number format: +1234567890"
    )
    address = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Physical address (max 500 characters)"
    )
    age = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Age in years (0-150)"
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        help_text="Profile picture (JPG, PNG, GIF, WebP - max 5MB, 2048x2048px)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.name} ({self.email})"

    def clean(self):
        """Custom validation using our validators"""
        super().clean()
        
        if self.name:
            validate_name(self.name)
        
        if self.email:
            validate_email(self.email)
        
        if self.phone_number:
            validate_phone(self.phone_number)
        
        if self.address:
            validate_address(self.address)
        
        if self.age is not None:
            validate_age(self.age)
        
        if self.profile_picture:
            validate_image(self.profile_picture)

    def delete(self, *args, **kwargs):
        """Override delete to remove profile picture file"""
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)
