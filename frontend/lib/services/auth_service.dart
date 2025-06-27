import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class AuthService {
  static const String _authStatusKey = 'auth_status';
  static const String _apiKeyInfoKey = 'api_key_info';
  static const String _lastValidatedKey = 'last_validated';
  
  // Cache duration for API key validation (1 hour)
  static const Duration _validationCacheDuration = Duration(hours: 1);
  
  // Check if the API key is valid and authenticated
  static Future<bool> isAuthenticated() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Check cached auth status
      final lastValidated = prefs.getString(_lastValidatedKey);
      if (lastValidated != null) {
        final lastValidatedTime = DateTime.parse(lastValidated);
        final now = DateTime.now();
        
        // If validated within cache duration, use cached result
        if (now.difference(lastValidatedTime) < _validationCacheDuration) {
          return prefs.getBool(_authStatusKey) ?? false;
        }
      }
      
      // Validate with server
      return await _validateAndCache();
    } catch (e) {
      if (kDebugMode) {
        print('Auth check failed: $e');
      }
      return false;
    }
  }
  
  // Validate API key with server and cache result
  static Future<bool> _validateAndCache() async {
    try {
      final result = await ApiService.validateApiKey();
      final prefs = await SharedPreferences.getInstance();
      
      final isValid = result['valid'] == true;
      
      // Cache the result
      await prefs.setBool(_authStatusKey, isValid);
      await prefs.setString(_lastValidatedKey, DateTime.now().toIso8601String());
      
      if (isValid && result.containsKey('key_name')) {
        // Cache API key info
        await prefs.setString(_apiKeyInfoKey, jsonEncode({
          'key_name': result['key_name'],
          'permissions': result['permissions'],
          'rate_limit': result['rate_limit'],
        }));
      }
      
      return isValid;
    } catch (e) {
      if (kDebugMode) {
        print('API key validation failed: $e');
      }
      
      // Cache negative result for a shorter duration
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_authStatusKey, false);
      await prefs.setString(_lastValidatedKey, DateTime.now().toIso8601String());
      
      return false;
    }
  }
  
  // Get cached API key information
  static Future<Map<String, dynamic>?> getCachedApiKeyInfo() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final infoJson = prefs.getString(_apiKeyInfoKey);
      
      if (infoJson != null) {
        return jsonDecode(infoJson);
      }
    } catch (e) {
      if (kDebugMode) {
        print('Failed to get cached API key info: $e');
      }
    }
    return null;
  }
  
  // Get fresh API key information from server
  static Future<Map<String, dynamic>?> getApiKeyInfo() async {
    try {
      final result = await ApiService.getApiKeyInfo();
      
      // Cache the result
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_apiKeyInfoKey, jsonEncode({
        'key_name': result['key_name'],
        'key_prefix': result['key_prefix'],
        'permissions': result['permissions'],
        'rate_limit': result['rate_limit'],
        'is_active': result['is_active'],
        'created_at': result['created_at'],
        'last_used': result['last_used'],
        'expires_at': result['expires_at'],
      }));
      
      return result;
    } catch (e) {
      if (kDebugMode) {
        print('Failed to get API key info: $e');
      }
      return null;
    }
  }
  
  // Force refresh of authentication status
  static Future<bool> refreshAuth() async {
    try {
      // Clear cached data
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_authStatusKey);
      await prefs.remove(_lastValidatedKey);
      
      // Validate fresh
      return await _validateAndCache();
    } catch (e) {
      if (kDebugMode) {
        print('Auth refresh failed: $e');
      }
      return false;
    }
  }
  
  // Clear all cached authentication data
  static Future<void> clearAuthCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_authStatusKey);
      await prefs.remove(_apiKeyInfoKey);
      await prefs.remove(_lastValidatedKey);
    } catch (e) {
      if (kDebugMode) {
        print('Failed to clear auth cache: $e');
      }
    }
  }
  
  // Check if user has specific permission
  static Future<bool> hasPermission(String resource, String action) async {
    try {
      final info = await getCachedApiKeyInfo();
      if (info == null) return false;
      
      final permissions = info['permissions'] as Map<String, dynamic>?;
      if (permissions == null) return false;
      
      final resourcePermissions = permissions[resource] as List<dynamic>?;
      if (resourcePermissions == null) return false;
      
      return resourcePermissions.contains(action) || resourcePermissions.contains('admin');
    } catch (e) {
      if (kDebugMode) {
        print('Permission check failed: $e');
      }
      return false;
    }
  }
  
  // Get rate limit information
  static Future<int?> getRateLimit() async {
    try {
      final info = await getCachedApiKeyInfo();
      return info?['rate_limit'] as int?;
    } catch (e) {
      if (kDebugMode) {
        print('Failed to get rate limit: $e');
      }
      return null;
    }
  }
}
