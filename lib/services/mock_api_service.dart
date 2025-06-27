import 'dart:io';
import '../models/user.dart';

// just until I create  backend
class MockApiService {
  static final List<User> _users = [
    User(
      id: 1,
      name: 'Clark Kent',
      email: 'clark.kent@example.com',
      phoneNumber: '1234567890',
      address: '123 Main St, metropolis, State',
      age: 25,
    ),
    User(
      id: 2,
      name: 'lois lane',
      email: 'lane@example.com',
      phoneNumber: '0987654321',
      address: '456 Oak Ave, Town, State',
      age: 30,
    ),
    User(
      id: 3,
      name: 'Jimmy olson',
      email: 'olson@example.com',
      age: 35,
    ),
  ];

  static int _nextId = 4;

  // Get all users with pagination
  static Future<Map<String, dynamic>> getUsers({int page = 1, int limit = 10}) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    final startIndex = (page - 1) * limit;
    final paginatedUsers = _users.skip(startIndex).take(limit).toList();

    return {
      'users': paginatedUsers,
      'total': _users.length,
      'page': page,
      'total_pages': (_users.length / limit).ceil(),
    };
  }

  // Create a new user
  static Future<User> createUser(User user, {File? profileImage}) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    final newUser = user.copyWith(id: _nextId++);
    _users.add(newUser);
    return newUser;
  }

  // Update an existing user
  static Future<User> updateUser(User user, {File? profileImage}) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    final index = _users.indexWhere((u) => u.id == user.id);
    if (index == -1) {
      throw Exception('User not found');
    }

    _users[index] = user;
    return user;
  }

  // Delete a user
  static Future<void> deleteUser(int userId) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    final index = _users.indexWhere((u) => u.id == userId);
    if (index == -1) {
      throw Exception('User not found');
    }

    _users.removeAt(index);
  }

  // Get a single user by ID
  static Future<User> getUser(int userId) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    final user = _users.firstWhere(
      (u) => u.id == userId,
      orElse: () => throw Exception('User not found'),
    );
    return user;
  }
}
