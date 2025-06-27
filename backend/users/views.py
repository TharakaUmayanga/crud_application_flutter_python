from django.shortcuts import render
from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import User, APIKey
from .serializers import UserSerializer, UserListSerializer
from .permissions import HasAPIKeyPermission, APIKeyRateLimit, ResourcePermission
from .authentication import RateLimitMixin
from .error_utils import validation_error_response, success_response, error_response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class UserListCreateView(generics.ListCreateAPIView, RateLimitMixin):
    """
    API endpoint for listing and creating users
    GET: List all users with pagination
    POST: Create a new user
    Requires API key authentication
    """
    queryset = User.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = CustomPagination
    permission_classes = [HasAPIKeyPermission, APIKeyRateLimit]
    permission_resource = 'users'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        
        # Add search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        # Add ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new user with proper error handling"""
        try:
            # Debug: Print received data
            print(f"Received data: {request.data}")
            print(f"Received files: {request.FILES}")
            
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save()
                    return success_response(
                        message='User created successfully',
                        data=UserSerializer(user, context={'request': request}).data,
                        status_code=status.HTTP_201_CREATED
                    )
                else:
                    print(f"Serializer errors: {serializer.errors}")
                    return validation_error_response(
                        message='Validation failed',
                        errors=serializer.errors
                    )
        except Exception as e:
            print(f"Exception in create: {e}")
            return error_response(
                message='An error occurred while creating the user',
                error_details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView, RateLimitMixin):
    """
    API endpoint for retrieving, updating, and deleting a specific user
    GET: Retrieve user details
    PUT/PATCH: Update user
    DELETE: Delete user
    Requires API key authentication
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [HasAPIKeyPermission, APIKeyRateLimit]
    permission_resource = 'users'

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific user"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'message': 'User retrieved successfully',
                'user': serializer.data
            })
        except User.DoesNotExist:
            return Response(
                {
                    'message': 'User not found',
                    'error': 'The requested user does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        """Update a user with proper error handling"""
        try:
            # Debug: Print received data
            print(f"Update - Received data: {request.data}")
            print(f"Update - Received files: {request.FILES}")
            
            with transaction.atomic():
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                
                # Store old profile picture for cleanup if needed
                old_profile_picture = instance.profile_picture
                
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                if serializer.is_valid():
                    user = serializer.save()
                    
                    # Clean up old profile picture if a new one was uploaded
                    if old_profile_picture and user.profile_picture != old_profile_picture:
                        try:
                            old_profile_picture.delete(save=False)
                        except:
                            pass  # Ignore errors in file deletion
                    
                    return success_response(
                        message='User updated successfully',
                        data=serializer.data
                    )
                else:
                    print(f"Update serializer errors: {serializer.errors}")
                    return validation_error_response(
                        message='Validation failed',
                        errors=serializer.errors
                    )
        except User.DoesNotExist:
            return error_response(
                message='User not found',
                error_details='The requested user does not exist',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='An error occurred while updating the user',
                error_details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """Delete a user with proper error handling"""
        try:
            instance = self.get_object()
            user_name = instance.name
            instance.delete()
            return success_response(
                message=f'User "{user_name}" deleted successfully'
            )
        except User.DoesNotExist:
            return error_response(
                message='User not found',
                error_details='The requested user does not exist',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='An error occurred while deleting the user',
                error_details=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def api_key_info(request):
    """
    Get information about the current API key being used.
    Does not expose the actual key value.
    """
    if not hasattr(request, 'auth') or not isinstance(request.auth, APIKey):
        return Response(
            {'error': 'No valid API key provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    api_key = request.auth
    
    return Response({
        'key_name': api_key.key_name,
        'key_prefix': api_key.key_prefix,
        'permissions': api_key.permissions,
        'rate_limit': api_key.rate_limit,
        'is_active': api_key.is_active,
        'created_at': api_key.created_at,
        'last_used': api_key.last_used,
        'expires_at': api_key.expires_at,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_api_key(request):
    """
    Validate an API key and return its information.
    Used for testing API key validity.
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    
    if not auth_header:
        return Response(
            {'valid': False, 'error': 'No authorization header provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        auth_type, api_key = auth_header.split(' ', 1)
        if auth_type.lower() != 'apikey':
            return Response(
                {'valid': False, 'error': 'Invalid authorization type'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except ValueError:
        return Response(
            {'valid': False, 'error': 'Invalid authorization format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        prefix = api_key[:8]
        api_key_obj = APIKey.objects.get(key_prefix=prefix, is_active=True)
        
        if api_key_obj.verify_key(api_key):
            return Response({
                'valid': True,
                'key_name': api_key_obj.key_name,
                'permissions': api_key_obj.permissions,
                'rate_limit': api_key_obj.rate_limit,
            })
        else:
            return Response(
                {'valid': False, 'error': 'Invalid API key'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except APIKey.DoesNotExist:
        return Response(
            {'valid': False, 'error': 'API key not found'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'valid': False, 'error': 'Validation error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
