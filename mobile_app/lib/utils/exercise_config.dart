
import 'app_language.dart';

class AngleTarget {

  final double minAngle;
  final double maxAngle;
  final String label;
  final bool trackElbow;

  const AngleTarget({

    required this.minAngle,
    required this.maxAngle,
    required this.label,
    this.trackElbow = false,

  });
}

class ExerciseConfig {

  static String displayName(String exerciseKey, AppLanguage language) {
    switch (exerciseKey) {

      case 'squat':

        return 'Squat';

      case 'lunge':

        return 'Lunge';

      case 'knee_pushup':

        return language == AppLanguage.tr ? 'Diz Üstü Şınav' : 'Knee Push-Up';

      case 'bridge':

        return language == AppLanguage.tr ? 'Köprü' : 'Bridge';

      default:

        return exerciseKey;
    }

  }

  static double predictionThreshold(String exerciseKey) {

    return exerciseKey == 'squat' ? 0.35 : 0.5;

  }


  /// Hibrit skor için daha sıkı eşikler.
  static double strictThreshold(String exerciseKey) {

    switch (exerciseKey) {

      case 'squat':

        return 0.62;

      case 'lunge':

        return 0.64;

      case 'knee_pushup':

        return 0.66;

      case 'bridge':

        return 0.63;

      default:

        return 0.64;
    }

  }

  /// 0..1 arası kural tabanlı form kalitesi.
  static double ruleBasedQuality({

    required String exerciseKey,
    required double leftKnee,
    required double rightKnee,
    required double leftElbow,
    required double rightElbow,
  }) {

    double clamp01(double v) => v < 0 ? 0 : (v > 1 ? 1 : v);


    final kneeAvg = (leftKnee + rightKnee) / 2;
    final kneeDiff = (leftKnee - rightKnee).abs();
    final elbowAvg = (leftElbow + rightElbow) / 2;
    final elbowDiff = (leftElbow - rightElbow).abs();


    switch (exerciseKey) {

      case 'squat':
        final depth = 1 - ((kneeAvg - 100).abs() / 70);
        final symmetry = 1 - (kneeDiff / 40);
        return clamp01((depth * 0.65) + (symmetry * 0.35));

      case 'lunge':
        final frontLeg = 1 - ((kneeAvg - 95).abs() / 65);
        final asymmetryDesired = (kneeDiff / 35);
        return clamp01((frontLeg * 0.7) + (asymmetryDesired * 0.3));

      case 'knee_pushup':
        final elbowRange = 1 - ((elbowAvg - 95).abs() / 70);
        final symmetry = 1 - (elbowDiff / 35);
        return clamp01((elbowRange * 0.7) + (symmetry * 0.3));

      case 'bridge':
        final kneeBand = 1 - ((kneeAvg - 110).abs() / 55);
        final symmetry = 1 - (kneeDiff / 30);
        return clamp01((kneeBand * 0.6) + (symmetry * 0.4));

      default:
        return 0.5;
    }

  }

  static AngleTarget? angleTarget(String exerciseKey, AppLanguage language) {

    switch (exerciseKey) {

      case 'squat':
        return AngleTarget(
          minAngle: 70,
          maxAngle: 110,
          label: language == AppLanguage.tr ? 'Diz' : 'Knee',
        );

      case 'lunge':
        return AngleTarget(
          minAngle: 75,
          maxAngle: 105,
          label: language == AppLanguage.tr ? 'Ön diz' : 'Front knee',
        );

      case 'knee_pushup':
        return AngleTarget(
          minAngle: 70,
          maxAngle: 120,
          label: language == AppLanguage.tr ? 'Dirsek' : 'Elbow',
          trackElbow: true,
        );

      case 'bridge':
        return AngleTarget(
          minAngle: 90,
          maxAngle: 135,
          label: language == AppLanguage.tr ? 'Diz' : 'Knee',
        );

      default:
        return null;
    }

  }

  static bool supportsRepCount(String exerciseKey) {

    return exerciseKey == 'squat' || exerciseKey == 'lunge';

  }

  /// Ayakta / dinlenme — bu fazda ML sonucu gösterilmez.
  static bool isStandingIdle({

    required String exerciseKey,
    required double leftKnee,
    required double rightKnee,
    required double leftElbow,
    required double rightElbow,
  }) {

    const straightLeg = 158.0;
    final legsStraight =
        leftKnee > straightLeg && rightKnee > straightLeg;

    switch (exerciseKey) {

      case 'squat':

      case 'lunge':

      case 'bridge':

        return legsStraight;

      case 'knee_pushup':
        const straightArm = 155.0;
        final armsStraight =
            leftElbow > straightArm && rightElbow > straightArm;
        return legsStraight && armsStraight;


      default:
        return legsStraight;
    }

  }

  /// Gerçek egzersiz hareketi içinde mi (model bu fazda çalışır).
  static bool isInActivePhase({

    required String exerciseKey,
    required double leftKnee,
    required double rightKnee,
    required double leftElbow,
    required double rightElbow,
  }) {

    if (isStandingIdle(
      exerciseKey: exerciseKey,
      leftKnee: leftKnee,
      rightKnee: rightKnee,
      leftElbow: leftElbow,
      rightElbow: rightElbow,
    )) {

      return false;
    }


    final kneeMin = leftKnee < rightKnee ? leftKnee : rightKnee;
    final kneeAvg = (leftKnee + rightKnee) / 2;
    final elbowAvg = (leftElbow + rightElbow) / 2;
    final kneeAsymmetry = (leftKnee - rightKnee).abs();


    switch (exerciseKey) {

      case 'squat':
        return kneeMin < 152;
      case 'lunge':
        return kneeMin < 135 || kneeAsymmetry > 22;
      case 'knee_pushup':
        final onKnees = leftKnee < 150 || rightKnee < 150;
        return onKnees && elbowAvg < 168;
      case 'bridge':
        return kneeAvg < 150 && kneeAvg > 65;
      default:
        return true;
    }

  }

  static String idleMessage(String exerciseKey, AppLanguage language) {

    switch (exerciseKey) {

      case 'squat':
        return language == AppLanguage.tr
            ? 'Squat için çömelin, ayakta beklemeyin.'
            : 'Start squatting instead of standing still.';

      case 'lunge':
        return language == AppLanguage.tr
            ? 'Lunge pozisyonuna geçin.'
            : 'Move into a lunge position.';

      case 'knee_pushup':
        return language == AppLanguage.tr
            ? 'Dizleriniz üzerinde şınav pozisyonuna geçin.'
            : 'Move into a knee push-up position.';

      case 'bridge':
        return language == AppLanguage.tr
            ? 'Sırt üstü köprü pozisyonuna geçin.'
            : 'Move into a bridge position.';

      default:
        return language == AppLanguage.tr
            ? 'Egzersiz pozisyonuna geçin.'
            : 'Move into the exercise position.';

    }
  }


  /// Egzersize özel kısa ipucları (yanlış formda olduğunu anlatma).
  static String? formTip({

    required String exerciseKey,
    required AppLanguage language,
    required double leftKnee,
    required double rightKnee,
    required double leftElbow,
    required double rightElbow,
    required bool isCorrect,
  }) {

    if (isCorrect) return null;


    final kneeAvg = (leftKnee + rightKnee) / 2;
    final elbowAvg = (leftElbow + rightElbow) / 2;
    final kneeDiff = (leftKnee - rightKnee).abs();

    switch (exerciseKey) {

      case 'squat':
        if (kneeAvg > 155) {

          return language == AppLanguage.tr
              ? 'Biraz daha derin squat yapın lütfen.'
              : 'Go a little deeper in the squat please.';
        }

        if (kneeAvg < 55) {

          return language == AppLanguage.tr
              ? 'Dizleri çok fazla kapatmayın.'
              : 'Do not close your knees too much.';
        }

        if (kneeDiff > 20) {

          return language == AppLanguage.tr
              ? 'Sol ve sağ dizleri hizalı tutun.'
              : 'Keep left and right knees aligned.';
        }

        return language == AppLanguage.tr
            ? 'Sırtınızı dik tutun, dizler ayak parmaklarını geçmesin.'
            : 'Keep your back upright, knees behind toes.';


      case 'lunge':
        if (kneeAvg > 150) {

          return language == AppLanguage.tr
              ? 'Ön bacağınızı lütfen biraz daha bükün.'
              : 'Bend your front leg a bit more.';
        }


        if (kneeDiff > 25) {

          return language == AppLanguage.tr
              ? 'Ön diziniz 90° civarında olmalı.'
              : 'Front knee should be around 90°.';
        }

        return language == AppLanguage.tr
            ? 'Gövdeyi dik tutun, arka diziniz yere yaklaşmasın.'
            : 'Keep torso upright, avoid dropping rear knee too much.';


      case 'knee_pushup':
        if (elbowAvg > 155) {

          return language == AppLanguage.tr
              ? 'Göğsünüzü yere biraz daha yaklaştırın.'
              : 'Lower your chest closer to the floor.';
        }

        if (elbowAvg < 55) {

          return language == AppLanguage.tr
              ? 'Dirseklerinizi tam kilitlemeyin.'
              : 'Do not fully lock your elbows.';
        }

        return language == AppLanguage.tr
            ? 'Karın kaslarını daha iyi sıkın, kalça düşmesin.'
            : 'Engage your core and avoid hip drop.';


      case 'bridge':
        if (kneeAvg < 80) {

          return language == AppLanguage.tr
              ? 'Dizlerinizi biraz daha açın.'
              : 'Open your knees a little more.';
        }

        if (kneeAvg > 145) {

          return language == AppLanguage.tr
              ? 'Kalçanızı omuz hizasına kaldırın.'
              : 'Lift hips up toward shoulder level.';
        }

        return language == AppLanguage.tr
            ? 'Kalçanızı yukarıda tutun, belinizi aşırı çukurlaştırmayın.'
            : 'Keep hips elevated and avoid over-arching your back.';


      default:
        return null;
    }

  }

  static String voiceMessage({

    required AppLanguage language,
    required bool isCorrect,
    required String? tip,
    required bool bodyVisible,
    required bool inActivePhase,
  }) {

    if (!bodyVisible) {

      return language == AppLanguage.tr
          ? 'Lütfen tüm vücudunuzun kadraja girmesini sağlayın.'
          : 'Keep your full body in frame.';
    }

    if (!inActivePhase) {

      return language == AppLanguage.tr

          ? 'Egzersize başlayabilirsiniz.'
          : 'Start the exercise.';
    }

    if (isCorrect) return language == AppLanguage.tr ? 'Form doğru.' : 'Good form.';

    return tip ?? (language == AppLanguage.tr ? 'Formu düzeltin.' : 'Fix your form.');
    
  }
}
