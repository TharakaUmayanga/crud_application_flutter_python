import 'package:flutter/material.dart';
import 'screens/user_list_screen.dart';

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'User CRUD Web Application',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 2,
        ),
      ),
      home: const ResponsiveWrapper(child: UserListScreen()),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ResponsiveWrapper extends StatelessWidget {
  final Widget child;
  
  const ResponsiveWrapper({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // For web, limit the maximum width for better UX
        if (constraints.maxWidth > 1200) {
          return Center(
            child: SizedBox(
              width: 1200,
              child: child,
            ),
          );
        }
        return child;
      },
    );
  }
}
