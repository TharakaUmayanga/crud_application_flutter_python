from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import APIKey
import hashlib


class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API key-based authentication.
    
    The client should include the API key in the request headers:
    Authorization: ApiKey your-api-key-here
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        try:
            auth_type, api_key = auth_header.split(' ', 1)
        except ValueError:
            return None
        
        if auth_type.lower() != 'apikey':
            return None
        
        return self.authenticate_credentials(api_key)
    
    def authenticate_credentials(self, api_key):
        """
        Authenticate the given API key.
        """
        if len(api_key) < 8:
            raise AuthenticationFailed('Invalid API key format.')
        
        # Get the prefix to find the API key record
        prefix = api_key[:8]
        
        try:
            api_key_obj = APIKey.objects.get(key_prefix=prefix, is_active=True)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key.')
        
        # Check if the key has expired
        if api_key_obj.expires_at and api_key_obj.expires_at < timezone.now():
            raise AuthenticationFailed('API key has expired.')
        
        # Verify the complete key
        if not api_key_obj.verify_key(api_key):
            raise AuthenticationFailed('Invalid API key.')
        
        # Update last used timestamp
        api_key_obj.last_used = timezone.now()
        api_key_obj.save(update_fields=['last_used'])
        
        # Return a tuple of (user, auth) where user can be None for API key auth
        # We'll use the API key object as the auth token
        return (None, api_key_obj)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'ApiKey'


class RateLimitMixin:
    """
    Mixin to add rate limiting functionality to views.
    """
    
    def check_rate_limit(self, api_key):
        """
        Check if the API key has exceeded its rate limit.
        This is a simple implementation - in production, you might want to use Redis or similar.
        """
        from django.core.cache import cache
        
        if not api_key:
            return True
        
        cache_key = f"rate_limit_{api_key.id}"
        current_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        cache_key_with_hour = f"{cache_key}_{current_hour.timestamp()}"
        
        current_count = cache.get(cache_key_with_hour, 0)
        
        if current_count >= api_key.rate_limit:
            return False
        
        # Increment the counter
        cache.set(cache_key_with_hour, current_count + 1, timeout=3600)  # 1 hour timeout
        return True