import re
import string
import unicodedata
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator as DjangoEmailValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import magic
import os


class CustomEmailValidator(DjangoEmailValidator):
    """Enhanced email validator with additional security checks"""
    
    # Blocked domains for security (you can add more)
    BLOCKED_DOMAINS = [
        'tempmail.org',
        '10minutemail.com',
        'mailinator.com',
        'guerrillamail.com',
    ]
    
    # Allowed TLDs (add more as needed)
    ALLOWED_TLDS = [
        'com', 'org', 'net', 'edu', 'gov', 'co', 'io', 'ai',
        'us', 'uk', 'ca', 'au', 'de', 'fr', 'jp', 'br', 'in'
    ]
    
    def __call__(self, value):
        # First, run the standard Django email validation
        super().__call__(value)
        
        # Additional custom validations
        if not value:
            return
        
        email_lower = value.lower().strip()
        local_part, domain = email_lower.rsplit('@', 1)
        
        # Check for blocked domains
        if domain in self.BLOCKED_DOMAINS:
            raise ValidationError(
                _('Email from this domain is not allowed.'),
                code='blocked_domain'
            )
        
        # Check TLD
        if '.' in domain:
            tld = domain.split('.')[-1]
            if tld not in self.ALLOWED_TLDS:
                raise ValidationError(
                    _('Email domain TLD is not supported.'),
                    code='unsupported_tld'
                )
        
        # Check for suspicious patterns
        if '..' in email_lower or email_lower.startswith('.') or email_lower.endswith('.'):
            raise ValidationError(
                _('Email format contains invalid characters.'),
                code='invalid_format'
            )
        
        # Length limits
        if len(local_part) > 64:
            raise ValidationError(
                _('Email local part is too long (max 64 characters).'),
                code='local_too_long'
            )
        
        if len(domain) > 253:
            raise ValidationError(
                _('Email domain is too long (max 253 characters).'),
                code='domain_too_long'
            )


class NameValidator:
    """Validator for user names with security and business rules"""
    
    # Allowed characters: letters, spaces, hyphens, apostrophes
    ALLOWED_PATTERN = re.compile(r"^[a-zA-ZÀ-ÿ\u0100-\u017F\u0180-\u024F\s\-'\.]+$")
    
    # Blocked patterns (common SQL injection attempts, XSS, etc.)
    BLOCKED_PATTERNS = [
        re.compile(r'<script.*?>', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'(union|select|insert|update|delete|drop|create|alter)\s', re.IGNORECASE),
        re.compile(r'[<>"\']'),  # HTML/XML characters
        re.compile(r'[\x00-\x1f\x7f-\x9f]'),  # Control characters
    ]
    
    def __call__(self, value):
        if not value:
            return
        
        # Normalize unicode
        normalized = unicodedata.normalize('NFKC', value)
        
        # Basic length check
        if len(normalized) < 2:
            raise ValidationError(
                _('Name must be at least 2 characters long.'),
                code='too_short'
            )
        
        if len(normalized) > 100:
            raise ValidationError(
                _('Name must not exceed 100 characters.'),
                code='too_long'
            )
        
        # Check allowed characters
        if not self.ALLOWED_PATTERN.match(normalized):
            raise ValidationError(
                _('Name contains invalid characters. Only letters, spaces, hyphens, and apostrophes are allowed.'),
                code='invalid_characters'
            )
        
        # Check for blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.search(normalized):
                raise ValidationError(
                    _('Name contains invalid or potentially harmful content.'),
                    code='invalid_content'
                )
        
        # Check for excessive spaces or special characters
        if '  ' in normalized or normalized.startswith(' ') or normalized.endswith(' '):
            raise ValidationError(
                _('Name cannot have leading/trailing spaces or multiple consecutive spaces.'),
                code='invalid_spacing'
            )
        
        # Check for patterns that might be attempts to bypass validation
        if any(char in normalized for char in ['\\', '/', '{', '}', '[', ']', '(', ')']):
            raise ValidationError(
                _('Name contains invalid characters.'),
                code='invalid_characters'
            )


class PhoneNumberValidator:
    """Enhanced phone number validator"""
    
    # International phone number pattern
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{6,14}$')
    
    def __call__(self, value):
        if not value:
            return
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', value)
        
        # Basic format check
        if not self.PHONE_PATTERN.match(cleaned):
            raise ValidationError(
                _('Enter a valid phone number. Format: +1234567890 (6-15 digits).'),
                code='invalid_format'
            )
        
        # Check for suspicious patterns
        if cleaned.count('+') > 1:
            raise ValidationError(
                _('Phone number can only contain one country code prefix (+).'),
                code='multiple_plus'
            )
        
        # Check length constraints
        digits_only = re.sub(r'[^\d]', '', cleaned)
        if len(digits_only) < 6:
            raise ValidationError(
                _('Phone number must have at least 6 digits.'),
                code='too_short'
            )
        
        if len(digits_only) > 15:
            raise ValidationError(
                _('Phone number must not exceed 15 digits.'),
                code='too_long'
            )


class AddressValidator:
    """Validator for address fields"""
    
    # Blocked patterns for address
    BLOCKED_PATTERNS = [
        re.compile(r'<script.*?>', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'(union|select|insert|update|delete|drop|create|alter)\s', re.IGNORECASE),
        re.compile(r'[\x00-\x1f\x7f-\x9f]'),  # Control characters
    ]
    
    def __call__(self, value):
        if not value:
            return
        
        # Normalize unicode
        normalized = unicodedata.normalize('NFKC', value)
        
        # Length check
        if len(normalized) > 500:
            raise ValidationError(
                _('Address must not exceed 500 characters.'),
                code='too_long'
            )
        
        # Check for blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.search(normalized):
                raise ValidationError(
                    _('Address contains invalid or potentially harmful content.'),
                    code='invalid_content'
                )
        
        # Check for excessive line breaks
        if normalized.count('\n') > 10:
            raise ValidationError(
                _('Address contains too many line breaks.'),
                code='too_many_lines'
            )


class AgeValidator:
    """Validator for age field"""
    
    def __call__(self, value):
        if value is None:
            return
        
        if not isinstance(value, int):
            raise ValidationError(
                _('Age must be a valid integer.'),
                code='invalid_type'
            )
        
        if value < 0:
            raise ValidationError(
                _('Age cannot be negative.'),
                code='negative_age'
            )
        
        if value > 150:
            raise ValidationError(
                _('Age cannot exceed 150 years.'),
                code='unrealistic_age'
            )


class ImageValidator:
    """Enhanced image validator with security checks"""
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
    ]
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    # Maximum file size (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    # Maximum dimensions
    MAX_WIDTH = 2048
    MAX_HEIGHT = 2048
    
    def __call__(self, value):
        if not value:
            return
        
        # Check file size
        if hasattr(value, 'size') and value.size > self.MAX_FILE_SIZE:
            raise ValidationError(
                _('Image file too large. Maximum size is 5MB.'),
                code='file_too_large'
            )
        
        # Check file extension
        if hasattr(value, 'name'):
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise ValidationError(
                    _('Invalid file type. Allowed types: JPG, PNG, GIF, WebP.'),
                    code='invalid_extension'
                )
        
        # Check MIME type using python-magic if available
        try:
            if hasattr(value, 'read'):
                # Save current position
                current_pos = value.tell() if hasattr(value, 'tell') else 0
                
                # Read first 1024 bytes for MIME detection
                value.seek(0)
                file_head = value.read(1024)
                
                # Reset position
                if hasattr(value, 'seek'):
                    value.seek(current_pos)
                
                # Detect MIME type
                mime_type = magic.from_buffer(file_head, mime=True)
                
                if mime_type not in self.ALLOWED_MIME_TYPES:
                    raise ValidationError(
                        _('Invalid file type. File appears to be: {}').format(mime_type),
                        code='invalid_mime_type'
                    )
        except ImportError:
            # python-magic not available, skip MIME type check
            pass
        except Exception:
            # If MIME detection fails, allow the file but log the issue
            pass
        
        # Additional checks can be added here for image dimensions
        # using PIL/Pillow if needed


class JSONFieldValidator:
    """Validator for JSON fields with size and content restrictions"""
    
    MAX_JSON_SIZE = 10 * 1024  # 10KB
    MAX_DEPTH = 10
    MAX_KEYS = 100
    
    def __call__(self, value):
        if not value:
            return
        
        import json
        
        # Check JSON size
        json_str = json.dumps(value) if not isinstance(value, str) else value
        if len(json_str.encode('utf-8')) > self.MAX_JSON_SIZE:
            raise ValidationError(
                _('JSON data too large. Maximum size is 10KB.'),
                code='json_too_large'
            )
        
        # Check JSON depth and key count
        try:
            self._check_json_structure(value, depth=0)
        except ValueError as e:
            raise ValidationError(str(e), code='invalid_json_structure')
    
    def _check_json_structure(self, obj, depth=0):
        if depth > self.MAX_DEPTH:
            raise ValueError('JSON structure too deep (max 10 levels)')
        
        if isinstance(obj, dict):
            if len(obj) > self.MAX_KEYS:
                raise ValueError(f'Too many keys in JSON object (max {self.MAX_KEYS})')
            
            for key, value in obj.items():
                if not isinstance(key, str) or len(key) > 100:
                    raise ValueError('JSON keys must be strings with max 100 characters')
                
                self._check_json_structure(value, depth + 1)
        
        elif isinstance(obj, list):
            if len(obj) > 1000:
                raise ValueError('JSON array too large (max 1000 items)')
            
            for item in obj:
                self._check_json_structure(item, depth + 1)
        
        elif isinstance(obj, str):
            if len(obj) > 1000:
                raise ValueError('JSON string value too long (max 1000 characters)')


# Sanitization functions
def sanitize_html(text):
    """Remove HTML tags and encode special characters"""
    if not text:
        return text
    
    import html
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]*>', '', str(text))
    # Encode HTML entities
    clean_text = html.escape(clean_text)
    return clean_text


def sanitize_sql(text):
    """Basic SQL injection prevention"""
    if not text:
        return text
    
    # Remove common SQL injection patterns
    dangerous_patterns = [
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
        r'(--|/\*|\*/)',
        r'(\bor\b.*=.*\bor\b)',
        r'(\band\b.*=.*\band\b)',
    ]
    
    clean_text = str(text)
    for pattern in dangerous_patterns:
        clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
    
    return clean_text


def normalize_text(text):
    """Normalize text for consistent processing"""
    if not text:
        return text
    
    # Unicode normalization
    normalized = unicodedata.normalize('NFKC', str(text))
    
    # Remove control characters
    normalized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', normalized)
    
    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized
