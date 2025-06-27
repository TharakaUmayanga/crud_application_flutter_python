from django.db import models
from django.core.validators import EmailValidator, RegexValidator
import os
import uuid


import uuid

def user_profile_picture_path(instance, filename):
    """Generate file path for user profile pictures"""
    # Use UUID if instance doesn't have an ID yet (during creation)
    identifier = instance.id if instance.id else str(uuid.uuid4())
    return f'profile_pictures/{identifier}/{filename}'


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
