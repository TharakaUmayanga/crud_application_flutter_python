from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.html import strip_tags
from .models import User, APIKey
from .validators import (
    sanitize_html, sanitize_sql, normalize_text,
    CustomEmailValidator, NameValidator, PhoneNumberValidator,
    AddressValidator, AgeValidator, ImageValidator
)
import re
import html
import bleach


class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'phone_number', 'address', 
            'age', 'profile_picture', 'profile_picture_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'profile_picture_url']
        
        # Add input size limits at serializer level
        extra_kwargs = {
            'name': {
                'max_length': 100,
                'min_length': 2,
                'allow_blank': False,
                'trim_whitespace': True,
            },
            'email': {
                'max_length': 254,
                'allow_blank': False,
            },
            'phone_number': {
                'max_length': 20,
                'allow_blank': True,
            },
            'address': {
                'max_length': 500,
                'allow_blank': True,
            },
            'age': {
                'min_value': 0,
                'max_value': 150,
            },
        }

    def get_profile_picture_url(self, obj):
        """Return the full URL for the profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def validate_email(self, value):
        """Enhanced email validation with sanitization"""
        if not value:
            raise serializers.ValidationError("Email is required.")
        
        # Sanitize and normalize
        cleaned_email = normalize_text(value.strip().lower())
        
        # Run custom validator
        validator = CustomEmailValidator()
        try:
            validator(cleaned_email)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
        
        # Additional business logic validation
        if cleaned_email.count('@') != 1:
            raise serializers.ValidationError("Invalid email format.")
        
        return cleaned_email

    def validate_name(self, value):
        """Enhanced name validation with sanitization"""
        if not value:
            raise serializers.ValidationError("Name is required.")
        
        # Sanitize input
        cleaned_name = sanitize_html(value)
        cleaned_name = sanitize_sql(cleaned_name)
        cleaned_name = normalize_text(cleaned_name)
        
        # Run custom validator
        validator = NameValidator()
        try:
            validator(cleaned_name)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
        
        # Additional checks for business rules
        if cleaned_name.lower() in ['admin', 'root', 'system', 'null', 'undefined']:
            raise serializers.ValidationError("Name cannot be a reserved word.")
        
        return cleaned_name

    def validate_phone_number(self, value):
        """Enhanced phone number validation"""
        if not value:
            return value
        
        # Sanitize input
        cleaned_phone = sanitize_html(value)
        cleaned_phone = normalize_text(cleaned_phone)
        
        # Run custom validator
        validator = PhoneNumberValidator()
        try:
            validator(cleaned_phone)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
        
        return cleaned_phone

    def validate_address(self, value):
        """Enhanced address validation"""
        if not value:
            return value
        
        # Sanitize input
        cleaned_address = sanitize_html(value)
        cleaned_address = sanitize_sql(cleaned_address)
        cleaned_address = normalize_text(cleaned_address)
        
        # Run custom validator
        validator = AddressValidator()
        try:
            validator(cleaned_address)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
        
        return cleaned_address

    def validate_age(self, value):
        """Enhanced age validation"""
        if value is None:
            return value
        
        # Run custom validator
        validator = AgeValidator()
        try:
            validator(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
        
        return value

    def validate_profile_picture(self, value):
        """Enhanced profile picture validation"""
        if not value:
            return value
        
        # Run custom validator
        validator = ImageValidator()
        try:
            validator(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
        
        return value

    def validate(self, data):
        """Perform cross-field validation and additional sanitization"""
        # Global input sanitization
        for field_name, field_value in data.items():
            if isinstance(field_value, str):
                # Apply HTML sanitization to all string fields
                data[field_name] = bleach.clean(
                    field_value,
                    tags=[],  # No HTML tags allowed
                    attributes={},  # No attributes allowed
                    strip=True,  # Strip disallowed tags
                    strip_comments=True  # Strip HTML comments
                )
        
        # Cross-field validation
        if 'age' in data and 'name' in data:
            # Business rule: if age is provided and < 13, name should indicate it's a minor
            if data.get('age', 0) < 13:
                # This is just an example - you can add your business rules here
                pass
        
        # Check for duplicate email
        email = data.get('email')
        if email:
            email = email.lower().strip()
            data['email'] = email
            
            if self.instance:
                # Update operation
                if email != getattr(self.instance, 'email', ''):
                    if User.objects.filter(email=email).exists():
                        raise serializers.ValidationError({
                            'email': 'A user with this email already exists.'
                        })
            else:
                # Create operation
                if User.objects.filter(email=email).exists():
                    raise serializers.ValidationError({
                        'email': 'A user with this email already exists.'
                    })
        
        # Validate request size (approximate)
        import json
        data_size = len(json.dumps(data, default=str).encode('utf-8'))
        max_request_size = 1024 * 1024  # 1MB
        
        if data_size > max_request_size:
            raise serializers.ValidationError(
                "Request data too large. Maximum size is 1MB."
            )
        
        return data


class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'phone_number', 
            'age', 'profile_picture_url', 'created_at'
        ]

    def get_profile_picture_url(self, obj):
        """Return the full URL for the profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None


class APIKeySerializer(serializers.ModelSerializer):
    """Enhanced serializer for API Key model with comprehensive validation"""
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'key_name', 'key_prefix', 'permissions', 
            'is_active', 'rate_limit', 'created_at', 
            'last_used', 'expires_at'
        ]
        read_only_fields = [
            'id', 'key_prefix', 'created_at', 'last_used'
        ]
        extra_kwargs = {
            'key_name': {
                'max_length': 100,
                'min_length': 3,
                'allow_blank': False,
                'trim_whitespace': True,
            },
            'rate_limit': {
                'min_value': 1,
                'max_value': 100000,
            },
        }
    
    def validate_key_name(self, value):
        """Enhanced validation for API key name"""
        if not value:
            raise serializers.ValidationError("API key name is required.")
        
        # Sanitize input
        cleaned_name = sanitize_html(value)
        cleaned_name = sanitize_sql(cleaned_name)
        cleaned_name = normalize_text(cleaned_name)
        
        # Basic format validation
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', cleaned_name):
            raise serializers.ValidationError(
                "API key name can only contain letters, numbers, spaces, hyphens, underscores, and dots."
            )
        
        # Length validation
        if len(cleaned_name) < 3:
            raise serializers.ValidationError("API key name must be at least 3 characters long.")
        
        if len(cleaned_name) > 100:
            raise serializers.ValidationError("API key name must not exceed 100 characters.")
        
        # Check for reserved names
        reserved_names = ['admin', 'root', 'system', 'api', 'key', 'test', 'default']
        if cleaned_name.lower() in reserved_names:
            raise serializers.ValidationError("API key name cannot be a reserved word.")
        
        return cleaned_name
    
    def validate_permissions(self, value):
        """Enhanced permissions validation"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Permissions must be a dictionary.")
        
        # Check JSON size limit
        import json
        permissions_size = len(json.dumps(value).encode('utf-8'))
        max_size = 10 * 1024  # 10KB
        
        if permissions_size > max_size:
            raise serializers.ValidationError("Permissions data too large (max 10KB).")
        
        # Validate structure
        valid_actions = ['read', 'write', 'delete', 'admin']
        valid_resources = ['users', 'api_keys', 'system']  # Add more as needed
        
        if len(value) == 0:
            raise serializers.ValidationError("At least one permission must be specified.")
        
        if len(value) > 20:
            raise serializers.ValidationError("Too many permission entries (max 20).")
        
        for resource, actions in value.items():
            # Validate resource name
            if not isinstance(resource, str):
                raise serializers.ValidationError("Resource names must be strings.")
            
            if len(resource) > 50:
                raise serializers.ValidationError(f"Resource name '{resource}' too long (max 50 chars).")
            
            if not re.match(r'^[a-zA-Z0-9_]+$', resource):
                raise serializers.ValidationError(
                    f"Resource name '{resource}' contains invalid characters. Only letters, numbers, and underscores allowed."
                )
            
            # For this example, we'll be flexible with resource names, but you can restrict to valid_resources
            
            # Validate actions
            if not isinstance(actions, list):
                raise serializers.ValidationError(
                    f"Permissions for '{resource}' must be a list."
                )
            
            if len(actions) == 0:
                raise serializers.ValidationError(
                    f"At least one action must be specified for resource '{resource}'."
                )
            
            if len(actions) > 10:
                raise serializers.ValidationError(
                    f"Too many actions for resource '{resource}' (max 10)."
                )
            
            for action in actions:
                if not isinstance(action, str):
                    raise serializers.ValidationError("Action names must be strings.")
                
                if action not in valid_actions:
                    raise serializers.ValidationError(
                        f"Invalid action '{action}' for resource '{resource}'. "
                        f"Valid actions are: {', '.join(valid_actions)}"
                    )
        
        return value
    
    def validate_rate_limit(self, value):
        """Validate rate limit value"""
        if value is None:
            return 1000  # Default rate limit
        
        if not isinstance(value, int):
            raise serializers.ValidationError("Rate limit must be an integer.")
        
        if value < 1:
            raise serializers.ValidationError("Rate limit must be at least 1 request per hour.")
        
        if value > 100000:
            raise serializers.ValidationError("Rate limit cannot exceed 100,000 requests per hour.")
        
        return value
    
    def validate(self, data):
        """Cross-field validation for API key"""
        # Sanitize all string fields
        for field_name, field_value in data.items():
            if isinstance(field_value, str):
                data[field_name] = bleach.clean(
                    field_value,
                    tags=[],
                    attributes={},
                    strip=True,
                    strip_comments=True
                )
        
        # Business logic validation
        permissions = data.get('permissions', {})
        rate_limit = data.get('rate_limit', 1000)
        
        # If admin permissions are granted, require higher rate limit
        has_admin = any('admin' in actions for actions in permissions.values())
        if has_admin and rate_limit < 1000:
            raise serializers.ValidationError({
                'rate_limit': 'Admin API keys require a minimum rate limit of 1000 requests/hour.'
            })
        
        # Check for duplicate key names
        key_name = data.get('key_name')
        if key_name:
            query = APIKey.objects.filter(key_name=key_name, is_active=True)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise serializers.ValidationError({
                    'key_name': 'An active API key with this name already exists.'
                })
        
        return data
