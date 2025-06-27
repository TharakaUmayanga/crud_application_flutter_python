"""
Security headers middleware for enhanced API security
"""

class SecurityHeadersMiddleware:
    """
    Middleware to add additional security headers to all responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        if not response.get('Strict-Transport-Security'):
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        if not response.get('Content-Security-Policy'):
            response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:"
        
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=(), usb=()'
        response['X-Permitted-Cross-Domain-Policies'] = 'none'
        response['Expect-CT'] = 'max-age=86400, enforce'
        
        return response
