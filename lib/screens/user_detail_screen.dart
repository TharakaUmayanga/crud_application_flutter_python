import 'package:flutter/material.dart';
import '../models/user.dart';
import 'user_form_screen.dart';

class UserDetailScreen extends StatelessWidget {
  final User user;

  const UserDetailScreen({super.key, required this.user});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('User Details'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => UserFormScreen(user: user),
                ),
              ).then((result) {
                if (result == true) {
                  Navigator.pop(context, true); // Go back and refresh
                }
              });
            },
            icon: const Icon(Icons.edit),
            tooltip: 'Edit User',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Profile Picture Section
            Center(
              child: Container(
                width: 150,
                height: 150,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.grey.shade300, width: 2),
                  color: Colors.grey.shade100,
                ),
                child: user.profilePicture != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(75),
                        child: Image.network(
                          user.profilePicture!,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return const Icon(Icons.person, size: 80, color: Colors.grey);
                          },
                        ),
                      )
                    : const Icon(Icons.person, size: 80, color: Colors.grey),
              ),
            ),
            const SizedBox(height: 32),

            // User Information Cards
            _buildInfoCard(
              icon: Icons.person,
              title: 'Name',
              value: user.name,
              color: Colors.blue,
            ),
            const SizedBox(height: 16),

            _buildInfoCard(
              icon: Icons.email,
              title: 'Email',
              value: user.email,
              color: Colors.green,
            ),
            const SizedBox(height: 16),

            if (user.phoneNumber != null && user.phoneNumber!.isNotEmpty)
              Column(
                children: [
                  _buildInfoCard(
                    icon: Icons.phone,
                    title: 'Phone Number',
                    value: user.phoneNumber!,
                    color: Colors.orange,
                  ),
                  const SizedBox(height: 16),
                ],
              ),

            if (user.address != null && user.address!.isNotEmpty)
              Column(
                children: [
                  _buildInfoCard(
                    icon: Icons.location_on,
                    title: 'Address',
                    value: user.address!,
                    color: Colors.red,
                  ),
                  const SizedBox(height: 16),
                ],
              ),

            if (user.age != null)
              Column(
                children: [
                  _buildInfoCard(
                    icon: Icons.cake,
                    title: 'Age',
                    value: user.age.toString(),
                    color: Colors.purple,
                  ),
                  const SizedBox(height: 16),
                ],
              ),

            // ID Information (for reference)
            _buildInfoCard(
              icon: Icons.fingerprint,
              title: 'User ID',
              value: user.id?.toString() ?? 'Unknown',
              color: Colors.grey,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
  }) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade600,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    value,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
