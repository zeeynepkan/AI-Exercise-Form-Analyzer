import 'package:flutter/material.dart';
import '../models/session_stats.dart';
import '../utils/app_language.dart';



class SessionSummaryPage extends StatelessWidget {

  final SessionStats stats;
  final AppLanguage language;

  const SessionSummaryPage(
    {
    super.key,
    required this.stats,
    required this.language,
  }
  );

  String _formatDuration(Duration d) 
  {
    final m = d.inMinutes;
    final s = d.inSeconds % 60;
    return language == AppLanguage.tr ? '$m dk $s sn' : '$m min $s sec';
  }

  String _text(String key) 
  {
    final tr = language == AppLanguage.tr;
    switch (key) {
      case 'session_summary':
        return tr ? 'Oturum Özeti' : 'Session Summary';
      case 'duration':
        return tr ? 'Süre' : 'Duration';
      case 'reps':
        return tr ? 'Tekrar' : 'Reps';
      case 'correct_form_rate':
        return tr ? 'Doğru form oranı' : 'Correct form rate';
      case 'analyzed_frames':
        return tr ? 'Analiz edilen kare' : 'Analyzed frames';
      case 'back_home':
        return tr ? 'Ana Sayfaya Dön' : 'Back to Home';
      default:
        return key;
    }
  }

  @override
  Widget build(BuildContext context) 
  {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text(_text('session_summary')),
        backgroundColor: Colors.greenAccent,
        foregroundColor: Colors.black,
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              stats.exerciseName,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.greenAccent,
                fontSize: 26,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            _SummaryCard(
              icon: Icons.timer_outlined,
              label: _text('duration'),
              value: _formatDuration(stats.duration),
            ),
            _SummaryCard(
              icon: Icons.repeat,
              label: _text('reps'),
              value: '${stats.reps}',
            ),
            _SummaryCard(
              icon: Icons.check_circle_outline,
              label: _text('correct_form_rate'),
              value: '${stats.formAccuracyPercent.toStringAsFixed(1)}%',
            ),
            _SummaryCard(
              icon: Icons.analytics_outlined,
              label: _text('analyzed_frames'),
              value: '${stats.analyzedFrames}',
            ),
            const Spacer(),
            FilledButton(
              onPressed: () 
              {
                Navigator.of(context).popUntil((route) => route.isFirst);
              },
              style: FilledButton.styleFrom(
                backgroundColor: Colors.greenAccent,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: Text(
                _text('back_home'),
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget 
{
  final IconData icon;
  final String label;
  final String value;

  const _SummaryCard(
    {
    required this.icon,
    required this.label,
    required this.value,
  }
  );

  @override
  Widget build(BuildContext context) 
  {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.5)),
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.greenAccent, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(color: Colors.white70, fontSize: 15),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
