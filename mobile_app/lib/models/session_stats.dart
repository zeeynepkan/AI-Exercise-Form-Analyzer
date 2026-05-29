class SessionStats {

  final String exerciseName;

  final String exerciseKey;

  final Duration duration;

  final int reps;

  final int analyzedFrames;

  final int correctFrames;

  const SessionStats({

    required this.exerciseName,

    required this.exerciseKey,

    required this.duration,

    required this.reps,

    required this.analyzedFrames,


    required this.correctFrames,

  });

  double get formAccuracyPercent {

    if (analyzedFrames == 0) return 0;
    return (correctFrames / analyzedFrames) * 100;

  }
  
}
