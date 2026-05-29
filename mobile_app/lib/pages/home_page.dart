
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'pose_page.dart';
import '../utils/app_language.dart';
import '../utils/exercise_config.dart';


class HomePage extends StatefulWidget {

  final bool isDarkMode;

  final ValueChanged<bool> onThemeChanged;

  const HomePage({

    super.key,

    required this.isDarkMode,
    required this.onThemeChanged,

  });


  @override
  State<HomePage> createState() => _HomePageState();
}


class _HomePageState extends State<HomePage> {


  AppLanguage selectedLanguage = AppLanguage.tr;

  static const _languagePrefKey = 'app_language';


  @override
  void initState() {

    super.initState();
    _loadSavedLanguage();

  }

  Future<void> _loadSavedLanguage() async {

    final prefs = await SharedPreferences.getInstance();

    final savedCode = prefs.getString(_languagePrefKey);

    if (!mounted || savedCode == null) return;

    final language = AppLanguage.values.firstWhere(
      (lang) => lang.code == savedCode,
      orElse: () => AppLanguage.tr,
    );

    setState(() => selectedLanguage = language);

  }

  Future<void> _saveLanguage(AppLanguage language) async {

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_languagePrefKey, language.code);

  }

  @override
  Widget build(BuildContext context) {

    final isDark = widget.isDarkMode;

    final bgColor = isDark ? Colors.black : const Color(0xFFF4F7F4);

    final cardColor = isDark ? Colors.grey[900] : Colors.white;

    final textColor = isDark ? Colors.white : Colors.black87;

    final accent = Colors.greenAccent;

    final exercises = [

      {
        "value": "squat",
        "icon": Icons.sports_gymnastics,
        "asset": "assets/exercise_icons/squat.svg",
      },

      {
        "value": "lunge",
        "icon": Icons.directions_run,
        "asset": "assets/exercise_icons/lunge.svg",
      },

      {
        "value": "knee_pushup",
        "icon": Icons.fitness_center,
        "asset": "assets/exercise_icons/knee_pushup.svg",
      },

      {
        "value": "bridge",
        "icon": Icons.self_improvement,
        "asset": "assets/exercise_icons/bridge.svg",
      },

    ];

    return Scaffold(

      backgroundColor: bgColor,
      appBar: AppBar(

        title: Text(

          selectedLanguage == AppLanguage.tr
              ? 'Egzersiz Form Analizi'
              : 'Exercise Form Analyzer',
        ),

        backgroundColor: accent,
        foregroundColor: Colors.black,
        actions: [

          IconButton(
            tooltip: selectedLanguage == AppLanguage.tr ? 'Tema değiştir' : 'Toggle theme',

            onPressed: () => widget.onThemeChanged(!isDark),

            icon: Icon(isDark ? Icons.light_mode : Icons.dark_mode),
          ),

          DropdownButtonHideUnderline(

            child: DropdownButton<AppLanguage>(

              value: selectedLanguage,
              dropdownColor: isDark ? Colors.black : Colors.white,
              iconEnabledColor: Colors.black,
              items: AppLanguage.values.map((lang) {

                return DropdownMenuItem(
                  value: lang,
                  child: Text(

                    lang.label,
                    style: TextStyle(

                      color: isDark ? Colors.greenAccent : Colors.black87,
                    ),

                  ),

                );

              }).toList(),

              onChanged: (value) {

                if (value == null) return;
                setState(() => selectedLanguage = value);
                _saveLanguage(value);

              },

            ),

          ),

          const SizedBox(width: 12),

        ],

      ),

      body: Padding(

        padding: const EdgeInsets.all(16),
        child: Column(

          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            const SizedBox(height: 10),
            Text(

              selectedLanguage == AppLanguage.tr
                  ? 'Analiz etmek istediğiniz egzersizi seçin'
                  : 'Select the exercise you want to analyze',
              style: TextStyle(

                color: textColor,
                fontSize: 24,
                fontWeight: FontWeight.bold,

              ),

            ),

            const SizedBox(height: 20),
            Expanded(

              child: GridView.builder(

                itemCount: exercises.length,
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 14,
                  mainAxisSpacing: 14,
                  childAspectRatio: 1,
                ),

                itemBuilder: (context, index) {

                  final exercise = exercises[index];


                  return GestureDetector(
                    onTap: () {

                      Navigator.push(

                        context,
                        MaterialPageRoute(

                          builder: (_) => PosePage(

                            selectedExercise: exercise["value"] as String,
                            language: selectedLanguage,

                          ),

                        ),

                      );

                    },
                    child: Container(

                      decoration: BoxDecoration(

                        color: cardColor,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: accent,
                          width: 2,

                        ),

                      ),

                      child: Column(

                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [

                          SvgPicture.asset(
                            exercise["asset"] as String,
                            width: 62,
                            height: 62,
                            colorFilter: ColorFilter.mode(
                              accent,
                              BlendMode.srcIn,

                            ),

                          ),
                          const SizedBox(height: 10),
                          Icon(
                            exercise["icon"] as IconData,
                            color: accent,
                            size: 24,
                          ),

                          const SizedBox(height: 12),
                          Text(
                            ExerciseConfig.displayName(
                              exercise["value"] as String,
                              selectedLanguage,
                            ),

                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: textColor,
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),

                          ),

                        ],

                      ),

                    ),
                  );

                },

              ),

            ),

          ],

        ),

      ),

    );

  }
  
}