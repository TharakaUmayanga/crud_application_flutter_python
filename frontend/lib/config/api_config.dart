class ApiConfig {
  // API Configuration
  static const String baseUrl = 'http://localhost:8000/api';
  
  // API Key for authentication
  // This is the Frontend App API key generated earlier
  static const String apiKey = 'K-J2K8MNgbWS3AsKOI6RCLUe3tKJWPk55VgUEg_HAnU';
  
  // Default headers for API requests
  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    'Authorization': 'ApiKey $apiKey',
  };
  
  // Headers for multipart requests (without Content-Type)
  static Map<String, String> get multipartHeaders => {
    'Authorization': 'ApiKey $apiKey',
  };
  
  // API endpoints
  static const String usersEndpoint = '/users/';
  static const String apiKeyValidateEndpoint = '/users/api-key/validate/';
  static const String apiKeyInfoEndpoint = '/users/api-key/info/';
  
  // Pagination defaults
  static const int defaultPageSize = 10;
  
  // Timeouts
  static const Duration requestTimeout = Duration(seconds: 30);
  static const Duration connectionTimeout = Duration(seconds: 10);
}

class ApiConstants {
  // HTTP Status Codes
  static const int statusOk = 200;
  static const int statusCreated = 201;
  static const int statusNoContent = 204;
  static const int statusBadRequest = 400;
  static const int statusUnauthorized = 401;
  static const int statusForbidden = 403;
  static const int statusNotFound = 404;
  static const int statusTooManyRequests = 429;
  static const int statusInternalServerError = 500;
  
  // Error messages
  static const String networkError = 'Network error occurred';
  static const String unauthorized = 'Unauthorized access';
  static const String forbidden = 'Access forbidden';
  static const String notFound = 'Resource not found';
  static const String rateLimitExceeded = 'Rate limit exceeded';
  static const String serverError = 'Server error occurred';
  static const String unknownError = 'Unknown error occurred';
}
