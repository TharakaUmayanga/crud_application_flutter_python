from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import APIKey


class HasAPIKeyPermission(BasePermission):
    """
    Custom permission class to check API key permissions.
    """
    
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        # Check if the request is authenticated with an API key
        if not hasattr(request, 'auth') or not isinstance(request.auth, APIKey):
            return False
        
        api_key = request.auth
        
        # Determine the resource and action based on the view and method
        resource = getattr(view, 'permission_resource', 'users')
        action = self.get_action_from_method(request.method)
        
        # Check if the API key has the required permission
        return api_key.has_permission(resource, action)
    
    def get_action_from_method(self, method):
        """
        Map HTTP methods to action names.
        """
        method_mapping = {
            'GET': 'read',
            'POST': 'write',
            'PUT': 'write',
            'PATCH': 'write',
            'DELETE': 'delete',
        }
        return method_mapping.get(method, 'read')


class APIKeyRateLimit(BasePermission):
    """
    Permission class to enforce rate limiting for API keys.
    """
    
    def has_permission(self, request, view):
        """
        Check if the API key hasn't exceeded its rate limit.
        """
        if not hasattr(request, 'auth') or not isinstance(request.auth, APIKey):
            return True  # Let other authentication handle this
        
        api_key = request.auth
        
        # Check rate limit using the mixin method
        from .authentication import RateLimitMixin
        rate_limit_checker = RateLimitMixin()
        
        if not rate_limit_checker.check_rate_limit(api_key):
            raise PermissionDenied("Rate limit exceeded. Please wait before making more requests.")
        
        return True


class ResourcePermission(BasePermission):
    """
    Permission class for resource-specific permissions.
    """
    
    def has_permission(self, request, view):
        """
        Check if the API key has permission for the specific resource.
        """
        if not hasattr(request, 'auth') or not isinstance(request.auth, APIKey):
            return False
        
        # Get the resource name from the view
        resource = getattr(view, 'permission_resource', 'default')
        action = self.get_action_from_method(request.method)
        
        return request.auth.has_permission(resource, action)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the API key has permission for the specific object.
        """
        if not hasattr(request, 'auth') or not isinstance(request.auth, APIKey):
            return False
        
        resource = getattr(view, 'permission_resource', 'default')
        action = self.get_action_from_method(request.method)
        
        return request.auth.has_permission(resource, action)
    
    def get_action_from_method(self, method):
        """
        Map HTTP methods to action names.
        """
        method_mapping = {
            'GET': 'read',
            'POST': 'write',
            'PUT': 'write',
            'PATCH': 'write',
            'DELETE': 'delete',
        }
        return method_mapping.get(method, 'read')