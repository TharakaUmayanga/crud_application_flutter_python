import json
import logging
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import SuspiciousOperation
import re

logger = logging.getLogger(__name__)


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive request validation and security
    """
    
    # Suspicious patterns to detect potential attacks (refined for fewer false positives)
    SUSPICIOUS_PATTERNS = [
        # SQL Injection patterns (more specific)
        re.compile(r'\bunion\s+select\b.*\bfrom\b', re.IGNORECASE),
        re.compile(r'\bdrop\s+table\b', re.IGNORECASE),
        re.compile(r'\bdelete\s+from\b.*\bwhere\b.*[\'"].*[\'"]', re.IGNORECASE),
        re.compile(r'\binsert\s+into\b.*\bvalues\b.*\([^)]*[\'"][^\'")]*[\'"][^)]*\)', re.IGNORECASE),
        re.compile(r'[\'"];.*--', re.IGNORECASE),  # SQL injection with comments
        
        # XSS patterns (more specific)
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript\s*:\s*[^;]+', re.IGNORECASE),
        re.compile(r'<iframe[^>]*src\s*=', re.IGNORECASE),
        re.compile(r'<object[^>]*data\s*=', re.IGNORECASE),
        
        # Path traversal patterns (more specific)
        re.compile(r'\.\.[\\/]\.\.[\\/]\.\.[\\/]'),  # Multiple directory traversals
        re.compile(r'[\\/]etc[\\/]passwd'),
        re.compile(r'[\\/]proc[\\/]self[\\/]'),
        
        # Command injection patterns (very specific)
        re.compile(r'[;&|`]\s*(rm\s+-rf|cat\s+\/etc|wget\s+http)', re.IGNORECASE),
        re.compile(r'\$\([^)]*rm[^)]*\)', re.IGNORECASE),
        
        # Template injection patterns (specific)
        re.compile(r'\{\{.*(__import__|eval|exec).*\}\}', re.IGNORECASE),
    ]
    
    # Allowed content types
    ALLOWED_CONTENT_TYPES = [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data',
        'text/plain',
    ]
    
    def process_request(self, request):
        """Process incoming request for validation"""
        
        # Skip validation for certain paths
        skip_paths = ['/admin/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Validate request size
        if hasattr(request, 'META'):
            content_length = request.META.get('CONTENT_LENGTH')
            if content_length:
                try:
                    content_length = int(content_length)
                    max_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 5 * 1024 * 1024)
                    
                    if content_length > max_size:
                        logger.warning(f"Request too large: {content_length} bytes from {self._get_client_ip(request)}")
                        return JsonResponse({
                            'error': 'Request too large',
                            'message': f'Maximum request size is {max_size} bytes'
                        }, status=413)
                except ValueError:
                    pass
        
        # Validate content type for POST/PUT/PATCH requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.content_type.split(';')[0] if request.content_type else ''
            if content_type and content_type not in self.ALLOWED_CONTENT_TYPES:
                logger.warning(f"Invalid content type: {content_type} from {self._get_client_ip(request)}")
                return JsonResponse({
                    'error': 'Invalid content type',
                    'message': f'Allowed content types: {", ".join(self.ALLOWED_CONTENT_TYPES)}'
                }, status=400)
        
        # Validate headers for suspicious content (skip common headers)
        skip_headers = [
            'HTTP_USER_AGENT', 'HTTP_ACCEPT', 'HTTP_ACCEPT_ENCODING', 
            'HTTP_ACCEPT_LANGUAGE', 'HTTP_CONNECTION', 'HTTP_HOST',
            'HTTP_AUTHORIZATION', 'HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH',
            'HTTP_CACHE_CONTROL', 'HTTP_PRAGMA', 'HTTP_REFERER'
        ]
        
        for header_name, header_value in request.META.items():
            if header_name.startswith('HTTP_') and header_name not in skip_headers:
                if self._contains_suspicious_content(str(header_value)):
                    logger.warning(f"Suspicious header content in {header_name} from {self._get_client_ip(request)}")
                    return JsonResponse({
                        'error': 'Invalid request',
                        'message': 'Request contains potentially harmful content'
                    }, status=400)
        
        # Validate query parameters
        for param_name, param_value in request.GET.items():
            if self._contains_suspicious_content(param_value):
                logger.warning(f"Suspicious query parameter {param_name} from {self._get_client_ip(request)}")
                return JsonResponse({
                    'error': 'Invalid request',
                    'message': 'Query parameters contain potentially harmful content'
                }, status=400)
        
        # Validate URL path
        if self._contains_suspicious_content(request.path):
            logger.warning(f"Suspicious URL path: {request.path} from {self._get_client_ip(request)}")
            return JsonResponse({
                'error': 'Invalid request',
                'message': 'URL contains potentially harmful content'
            }, status=400)
        
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Process view for additional validation"""
        
        # Skip validation for certain views
        if hasattr(view_func, '__name__') and view_func.__name__ in ['admin', 'static', 'media']:
            return None
        
        # Validate POST/PUT data for JSON requests
        if request.method in ['POST', 'PUT', 'PATCH'] and request.content_type == 'application/json':
            try:
                if hasattr(request, 'body') and request.body:
                    # Check if body contains suspicious content
                    body_str = request.body.decode('utf-8')
                    
                    if self._contains_suspicious_content(body_str):
                        logger.warning(f"Suspicious request body from {self._get_client_ip(request)}")
                        return JsonResponse({
                            'error': 'Invalid request',
                            'message': 'Request body contains potentially harmful content'
                        }, status=400)
                    
                    # Validate JSON structure
                    try:
                        json_data = json.loads(body_str)
                        if not self._validate_json_structure(json_data):
                            logger.warning(f"Invalid JSON structure from {self._get_client_ip(request)}")
                            return JsonResponse({
                                'error': 'Invalid request',
                                'message': 'JSON structure is invalid or too complex'
                            }, status=400)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from {self._get_client_ip(request)}")
                        return JsonResponse({
                            'error': 'Invalid JSON',
                            'message': 'Request body contains invalid JSON'
                        }, status=400)
            
            except UnicodeDecodeError:
                logger.warning(f"Invalid encoding in request body from {self._get_client_ip(request)}")
                return JsonResponse({
                    'error': 'Invalid encoding',
                    'message': 'Request body contains invalid character encoding'
                }, status=400)
        
        return None
    
    def _contains_suspicious_content(self, content):
        """Check if content contains suspicious patterns"""
        if not content:
            return False
        
        content_str = str(content)
        
        # Check against suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.search(content_str):
                return True
        
        # Check for control characters (except common ones)
        for char in content_str:
            if ord(char) < 32 and char not in ['\t', '\n', '\r']:
                return True
        
        # Check for excessive length
        if len(content_str) > 10000:  # 10KB limit for individual values
            return True
        
        return False
    
    def _validate_json_structure(self, data, depth=0, key_count=0):
        """Validate JSON structure for security"""
        max_depth = 10
        max_keys = 100
        max_array_length = 1000
        
        if depth > max_depth:
            return False
        
        if isinstance(data, dict):
            if len(data) > max_keys:
                return False
            
            for key, value in data.items():
                if not isinstance(key, str) or len(key) > 100:
                    return False
                
                if self._contains_suspicious_content(key):
                    return False
                
                if not self._validate_json_structure(value, depth + 1, key_count + len(data)):
                    return False
        
        elif isinstance(data, list):
            if len(data) > max_array_length:
                return False
            
            for item in data:
                if not self._validate_json_structure(item, depth + 1, key_count):
                    return False
        
        elif isinstance(data, str):
            if len(data) > 5000:  # 5KB limit for string values
                return False
            
            if self._contains_suspicious_content(data):
                return False
        
        return True
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def process_exception(self, request, exception):
        """Handle exceptions during request processing"""
        if isinstance(exception, SuspiciousOperation):
            logger.warning(f"Suspicious operation from {self._get_client_ip(request)}: {exception}")
            return JsonResponse({
                'error': 'Suspicious operation detected',
                'message': 'Request blocked for security reasons'
            }, status=400)
        
        return None
