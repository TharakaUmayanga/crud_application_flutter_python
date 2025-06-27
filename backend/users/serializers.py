from rest_framework import serializers
from .models import User, APIKey
import re


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

    def get_profile_picture_url(self, obj):
        """Return the full URL for the profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def validate_email(self, value):
        """Validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required.")
        
        # Email format validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Please enter a valid email address.")
        
        return value.lower()

    def validate_name(self, value):
        """Validate name field"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        
        return value.strip()

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value:
            # Remove any spaces or special characters except + and digits
            cleaned_phone = re.sub(r'[^\d+]', '', value)
            
            # Check if it matches the expected format
            phone_regex = r'^\+?1?\d{9,15}$'
            if not re.match(phone_regex, cleaned_phone):
                raise serializers.ValidationError(
                    "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
                )
            return cleaned_phone
        return value

    def validate_age(self, value):
        """Validate age field"""
        if value is not None:
            if value < 0 or value > 150:
                raise serializers.ValidationError("Age must be between 0 and 150.")
        return value

    def validate(self, data):
        """Perform cross-field validation"""
        # Check for duplicate email on update
        if self.instance:
            # This is an update operation
            if 'email' in data and data['email'] != self.instance.email:
                if User.objects.filter(email=data['email']).exists():
                    raise serializers.ValidationError({
                        'email': 'A user with this email already exists.'
                    })
        else:
            # This is a create operation
            if 'email' in data and User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError({
                    'email': 'A user with this email already exists.'
                })
        
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
    """Serializer for API Key model (without exposing the actual key)"""
    
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
    
    def validate_permissions(self, value):
        """Validate permissions format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Permissions must be a dictionary.")
        
        valid_actions = ['read', 'write', 'delete', 'admin']
        for resource, actions in value.items():
            if not isinstance(actions, list):
                raise serializers.ValidationError(
                    f"Permissions for '{resource}' must be a list."
                )
            for action in actions:
                if action not in valid_actions:
                    raise serializers.ValidationError(
                        f"Invalid action '{action}' for resource '{resource}'. "
                        f"Valid actions are: {', '.join(valid_actions)}"
                    )
        
        return value
