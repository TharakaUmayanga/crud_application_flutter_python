import 'dart:io';
import '../models/user.dart';
import '../config/app_config.dart';
import 'api_service.dart';
import 'mock_api_service.dart';

class UserService {
  // Get all users with pagination
  static Future<Map<String, dynamic>> getUsers({int page = 1, int limit = 10}) async {
    if (AppConfig.useMockData) {
      return await MockApiService.getUsers(page: page, limit: limit);
    } else {
      return await ApiService.getUsers(page: page, limit: limit);
    }
  }

  // Create a new user
  static Future<User> createUser(User user, {File? profileImage}) async {
    if (AppConfig.useMockData) {
      return await MockApiService.createUser(user, profileImage: profileImage);
    } else {
      return await ApiService.createUser(user, profileImage: profileImage);
    }
  }

  // Update an existing user
  static Future<User> updateUser(User user, {File? profileImage}) async {
    if (AppConfig.useMockData) {
      return await MockApiService.updateUser(user, profileImage: profileImage);
    } else {
      return await ApiService.updateUser(user, profileImage: profileImage);
    }
  }

  // Delete a user
  static Future<void> deleteUser(int userId) async {
    if (AppConfig.useMockData) {
      return await MockApiService.deleteUser(userId);
    } else {
      return await ApiService.deleteUser(userId);
    }
  }

  // Get a single user by ID
  static Future<User> getUser(int userId) async {
    if (AppConfig.useMockData) {
      return await MockApiService.getUser(userId);
    } else {
      return await ApiService.getUser(userId);
    }
  }
}
