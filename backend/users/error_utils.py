"""
Error formatting utilities for API responses
"""

from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError


def format_serializer_errors(serializer_errors):
    """
    Format DRF serializer errors for consistent frontend consumption
    Converts ErrorDetail objects to plain strings
    """
    formatted_errors = {}
    
    for field, errors in serializer_errors.items():
        if isinstance(errors, list):
            # Convert ErrorDetail objects to strings
            formatted_errors[field] = [str(error) for error in errors]
        else:
            # Handle single error
            formatted_errors[field] = [str(errors)]
    
    return formatted_errors


def validation_error_response(message, errors, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Create a standardized validation error response
    """
    return Response(
        {
            'success': False,
            'message': message,
            'errors': format_serializer_errors(errors) if hasattr(errors, 'items') else errors,
            'status_code': status_code
        },
        status=status_code
    )


def success_response(message, data=None, status_code=status.HTTP_200_OK):
    """
    Create a standardized success response
    """
    response_data = {
        'success': True,
        'message': message,
        'status_code': status_code
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status_code)


def error_response(message, error_details=None, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
    """
    Create a standardized error response
    """
    response_data = {
        'success': False,
        'message': message,
        'status_code': status_code
    }
    
    if error_details is not None:
        response_data['error'] = str(error_details)
    
    return Response(response_data, status=status_code)
