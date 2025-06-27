import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/user.dart';
import '../config/api_config.dart';

class ApiService {
  // Get all users with pagination
  static Future<Map<String, dynamic>> getUsers({int page = 1, int limit = 10}) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.usersEndpoint}?page=$page&page_size=$limit'),
        headers: ApiConfig.headers,
      ).timeout(ApiConfig.requestTimeout);

      if (response.statusCode == ApiConstants.statusOk) {
        final data = jsonDecode(response.body);
        
        // Handle null safety for the results array
        final resultsData = data['results'];
        List<User> users = [];
        
        if (resultsData != null && resultsData is List) {
          users = resultsData.map((json) => User.fromJson(json as Map<String, dynamic>)).toList();
        }
        
        return {
          'users': users,
          'total': data['count'] ?? 0,
          'page': data['current_page'] ?? page,
          'totalPages': data['total_pages'] ?? 1,
        };
      } else {
        throw _handleApiError(response);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('${ApiConstants.networkError}: $e');
    }
  }

  // Create a new user
  static Future<User> createUser(User user, {File? profileImage, Uint8List? webImageBytes, String? webImageName}) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('${ApiConfig.baseUrl}${ApiConfig.usersEndpoint}'));
      
      // Add authentication headers
      request.headers.addAll(ApiConfig.multipartHeaders);
      
      // Add user data
      request.fields['name'] = user.name;
      request.fields['email'] = user.email;
      if (user.phoneNumber != null) request.fields['phone_number'] = user.phoneNumber!;
      if (user.address != null) request.fields['address'] = user.address!;
      if (user.age != null) request.fields['age'] = user.age.toString();

      // Add profile image if provided
      if (kIsWeb && webImageBytes != null) {
        // For web platform
        request.files.add(http.MultipartFile.fromBytes(
          'profile_picture',
          webImageBytes,
          filename: webImageName ?? 'profile_picture.jpg',
        ));
      } else if (!kIsWeb && profileImage != null) {
        // For mobile platforms
        request.files.add(await http.MultipartFile.fromPath('profile_picture', profileImage.path));
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        // The backend returns the user data in a 'user' field
        if (data['user'] != null) {
          return User.fromJson(data['user'] as Map<String, dynamic>);
        } else {
          return User.fromJson(data as Map<String, dynamic>);
        }
      } else {
        throw _handleApiError(response);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('${ApiConstants.networkError}: $e');
    }
  }

  // Update an existing user
  static Future<User> updateUser(User user, {File? profileImage, Uint8List? webImageBytes, String? webImageName}) async {
    try {
      var request = http.MultipartRequest('PUT', Uri.parse('${ApiConfig.baseUrl}${ApiConfig.usersEndpoint}${user.id}/'));
      
      // Add authentication headers
      request.headers.addAll(ApiConfig.multipartHeaders);
      
      // Add user data
      request.fields['name'] = user.name;
      request.fields['email'] = user.email;
      if (user.phoneNumber != null) request.fields['phone_number'] = user.phoneNumber!;
      if (user.address != null) request.fields['address'] = user.address!;
      if (user.age != null) request.fields['age'] = user.age.toString();

      // Add profile image if provided
      if (kIsWeb && webImageBytes != null) {
        // For web platform
        request.files.add(http.MultipartFile.fromBytes(
          'profile_picture',
          webImageBytes,
          filename: webImageName ?? 'profile_picture.jpg',
        ));
      } else if (!kIsWeb && profileImage != null) {
        // For mobile platforms
        request.files.add(await http.MultipartFile.fromPath('profile_picture', profileImage.path));
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // The backend returns the user data in a 'user' field
        if (data['user'] != null) {
          return User.fromJson(data['user'] as Map<String, dynamic>);
        } else {
          return User.fromJson(data as Map<String, dynamic>);
        }
      } else {
        throw _handleApiError(response);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('${ApiConstants.networkError}: $e');
    }
  }

  // Delete a user
  static Future<void> deleteUser(int userId) async {
    try {
      final response = await http.delete(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.usersEndpoint}$userId/'),
        headers: ApiConfig.headers,
      ).timeout(ApiConfig.requestTimeout);

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw _handleApiError(response);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('${ApiConstants.networkError}: $e');
    }
  }

  // Get a single user by ID
  static Future<User> getUser(int userId) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.usersEndpoint}$userId/'),
        headers: ApiConfig.headers,
      ).timeout(ApiConfig.requestTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // The backend returns the user data in a 'user' field
        if (data['user'] != null) {
          return User.fromJson(data['user'] as Map<String, dynamic>);
        } else {
          return User.fromJson(data as Map<String, dynamic>);
        }
      } else {
        throw _handleApiError(response);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('${ApiConstants.networkError}: $e');
    }
  }

  // Validate API key
  static Future<Map<String, dynamic>> validateApiKey() async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.apiKeyValidateEndpoint}'),
        headers: ApiConfig.headers,
      ).timeout(ApiConfig.requestTimeout);

      if (response.statusCode == ApiConstants.statusOk) {
        return jsonDecode(response.body);
      } else {
        throw _handleApiError(response);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('${ApiConstants.networkError}: $e');
    }
  }

  // Get API key information
  static Future<Map<String, dynamic>> getApiKeyInfo() async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.apiKeyInfoEndpoint}'),
        headers: ApiConfig.headers,
      ).timeout(ApiConfig.requestTimeout);

      if (response.statusCode == ApiConstants.statusOk) {
        return jsonDecode(response.body);
      } else {
        throw _handleApiError(response);
      }
    } catch (e) {
      if (e is Exception) {
        rethrow;
      }
      throw Exception('${ApiConstants.networkError}: $e');
    }
  }

  // Private method to handle API errors
  static Exception _handleApiError(http.Response response) {
    String message;
    
    switch (response.statusCode) {
      case ApiConstants.statusUnauthorized:
        message = ApiConstants.unauthorized;
        break;
      case ApiConstants.statusForbidden:
        message = ApiConstants.forbidden;
        break;
      case ApiConstants.statusNotFound:
        message = ApiConstants.notFound;
        break;
      case ApiConstants.statusTooManyRequests:
        message = ApiConstants.rateLimitExceeded;
        break;
      case ApiConstants.statusInternalServerError:
        message = ApiConstants.serverError;
        break;
      default:
        message = '${ApiConstants.unknownError} (${response.statusCode})';
    }
    
    try {
      final errorData = jsonDecode(response.body);
      if (errorData['detail'] != null) {
        message = errorData['detail'];
      } else if (errorData['error'] != null) {
        message = errorData['error'];
      }
    } catch (e) {
      // If response body is not valid JSON, use the default message
    }
    
    return Exception(message);
  }
}
