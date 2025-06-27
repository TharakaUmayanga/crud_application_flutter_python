import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/user.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api'; // Change this to your backend URL
  
  // Get all users with pagination
  static Future<Map<String, dynamic>> getUsers({int page = 1, int limit = 10}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/users?page=$page&limit=$limit'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'users': (data['users'] as List).map((json) => User.fromJson(json)).toList(),
          'total': data['total'],
          'page': data['page'],
          'totalPages': data['total_pages'],
        };
      } else {
        throw Exception('Failed to load users: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Create a new user
  static Future<User> createUser(User user, {File? profileImage}) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/users'));
      
      // Add user data
      request.fields['name'] = user.name;
      request.fields['email'] = user.email;
      if (user.phoneNumber != null) request.fields['phone_number'] = user.phoneNumber!;
      if (user.address != null) request.fields['address'] = user.address!;
      if (user.age != null) request.fields['age'] = user.age.toString();

      // Add profile image if provided
      if (profileImage != null) {
        request.files.add(await http.MultipartFile.fromPath('profile_picture', profileImage.path));
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 201) {
        return User.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to create user: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Update an existing user
  static Future<User> updateUser(User user, {File? profileImage}) async {
    try {
      var request = http.MultipartRequest('PUT', Uri.parse('$baseUrl/users/${user.id}'));
      
      // Add user data
      request.fields['name'] = user.name;
      request.fields['email'] = user.email;
      if (user.phoneNumber != null) request.fields['phone_number'] = user.phoneNumber!;
      if (user.address != null) request.fields['address'] = user.address!;
      if (user.age != null) request.fields['age'] = user.age.toString();

      // Add profile image if provided
      if (profileImage != null) {
        request.files.add(await http.MultipartFile.fromPath('profile_picture', profileImage.path));
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return User.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to update user: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Delete a user
  static Future<void> deleteUser(int userId) async {
    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/users/$userId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to delete user: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Get a single user by ID
  static Future<User> getUser(int userId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/users/$userId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return User.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to load user: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}
