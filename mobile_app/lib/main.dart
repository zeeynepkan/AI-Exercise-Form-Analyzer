
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'pages/home_page.dart';

void main() {

  runApp(const ExerciseFormAnalyzerApp());
}


class ExerciseFormAnalyzerApp extends StatefulWidget {

  const ExerciseFormAnalyzerApp({super.key});


  @override
  State<ExerciseFormAnalyzerApp> createState() => _ExerciseFormAnalyzerAppState();

}

class _ExerciseFormAnalyzerAppState extends State<ExerciseFormAnalyzerApp> {

  static const _themePrefKey = 'app_theme_mode';

  ThemeMode _themeMode = ThemeMode.dark;


  @override
  void initState() {

    super.initState();
    _loadThemeMode();

  }

  Future<void> _loadThemeMode() async {

    final prefs = await SharedPreferences.getInstance();

    final savedMode = prefs.getString(_themePrefKey);


    if (!mounted || savedMode == null) return;

    setState(() {

      _themeMode = savedMode == 'light' ? ThemeMode.light : ThemeMode.dark;

    });

  }

  Future<void> _setDarkMode(bool isDarkMode) async {

    final prefs = await SharedPreferences.getInstance();

    await prefs.setString(_themePrefKey, isDarkMode ? 'dark' : 'light');

    if (!mounted) 
    return;

    setState(() {

      _themeMode = isDarkMode ? ThemeMode.dark : ThemeMode.light;

    });

  }

  @override
  Widget build(BuildContext context) {

    return 
    MaterialApp(

      debugShowCheckedModeBanner: false,
      title: 'Exercise Form Analyzer',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        useMaterial3: true,
      ),

      darkTheme: ThemeData(

        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.greenAccent,
          brightness: Brightness.dark,
        ),

        useMaterial3: true,
      ),

      themeMode: _themeMode,
      home: HomePage(

        isDarkMode: _themeMode != ThemeMode.light,
        onThemeChanged: _setDarkMode,
        
      ),

    );
  }
}