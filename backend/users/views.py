from django.shortcuts import render
from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import User
from .serializers import UserSerializer, UserListSerializer


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


class UserListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating users
    GET: List all users with pagination
    POST: Create a new user
    """
    queryset = User.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = CustomPagination

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
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save()
                    return Response(
                        {
                            'message': 'User created successfully',
                            'user': UserSerializer(user, context={'request': request}).data
                        },
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response(
                        {
                            'message': 'Validation failed',
                            'errors': serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            return Response(
                {
                    'message': 'An error occurred while creating the user',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a specific user
    GET: Retrieve user details
    PUT/PATCH: Update user
    DELETE: Delete user
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

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
                    
                    return Response({
                        'message': 'User updated successfully',
                        'user': serializer.data
                    })
                else:
                    return Response(
                        {
                            'message': 'Validation failed',
                            'errors': serializer.errors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except User.DoesNotExist:
            return Response(
                {
                    'message': 'User not found',
                    'error': 'The requested user does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'message': 'An error occurred while updating the user',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        """Delete a user with proper error handling"""
        try:
            instance = self.get_object()
            user_name = instance.name
            instance.delete()
            return Response(
                {
                    'message': f'User "{user_name}" deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {
                    'message': 'User not found',
                    'error': 'The requested user does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'message': 'An error occurred while deleting the user',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
