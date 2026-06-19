import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const QuintaFeiraApp());
}

class QuintaFeiraApp extends StatelessWidget {
  const QuintaFeiraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Quinta-Feira',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF00D4FF),
        scaffoldBackgroundColor: const Color(0xFF0A0A0F),
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFF00D4FF),
          secondary: const Color(0xFF00FF88),
          surface: const Color(0xFF1A1A2E),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0A0A0F),
          elevation: 0,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
