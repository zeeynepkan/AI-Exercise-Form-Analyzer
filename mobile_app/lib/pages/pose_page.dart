
import 'dart:async';
import 'dart:convert';
import 'dart:math';



import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';


import 'package:flutter/services.dart';
import 'package:flutter_mp_pose_landmarker/flutter_mp_pose_landmarker.dart';


import 'package:flutter_tts/flutter_tts.dart';


import '../models/session_stats.dart';


import '../utils/app_language.dart';
import '../utils/exercise_config.dart';


import 'session_summary_page.dart';

class PosePage extends StatefulWidget
 {

  final String selectedExercise;
  final AppLanguage language;

  const PosePage({

    super.key,
    required this.selectedExercise,
    required this.language,

  });

  @override
  State<PosePage> createState() => _PosePageState();

}

class _PosePageState extends State<PosePage> 
{

  List<PoseLandmarkPoint> landmarks = [];

  StreamSubscription<PoseLandMarker>? poseSubscription;




  double leftKneeAngle = 0;
  double rightKneeAngle = 0;
  double leftElbowAngle = 0;
  double rightElbowAngle = 0;
  double smoothingFactor = 0.2;



  List<double> currentModelInput = [];
  List<double> scalerMean = [];
  List<double> scalerScale = [];
  List<dynamic> mlpLayers = [];



  String predictionLabel = '';
  double predictionScore = 0;
  double modelScore = 0;
  double ruleScore = 0;
  String? currentTip;
  bool inActivePhase = false;



  List<double> predictionHistory = [];
  int predictionWindowSize = 20;



  final DateTime sessionStart = DateTime.now();
  int analyzedFrames = 0;
  int correctFrames = 0;
  int repCount = 0;
  bool repWasDown = false;
  bool sessionFinished = false;


  FlutterTts? _tts;
  String? _lastSpokenText;
  DateTime? _lastSpeakTime;


  @override
  void initState() 
  {

    super.initState();
    predictionLabel = _text('model_loading');
    initializePosePage();

  }

  Future<void> initializePosePage() async 
  {

    await _initTts();


    final granted = await PoseLandmarker.checkCameraPermission();
    if (!granted) 
    {

      await PoseLandmarker.requestCameraPermission();

    }

    await loadModelFiles();


    PoseLandmarker.setConfig(

      delegate: 0,
      model: 1,
      minPoseDetectionConfidence: 0.5,
      minPoseTrackingConfidence: 0.5,
      minPosePresenceConfidence: 0.5,

    );

    poseSubscription = PoseLandmarker.poseLandmarkStream.listen((pose) 
    
    {

      if (!mounted || sessionFinished) return;

      setState(() 
      {

        landmarks = pose.landmarks;

        if (landmarks.length == 33 && isFullBodyVisible(landmarks)) 
        {

          calculateExerciseAngles(landmarks);


          final features = extractFeatures(landmarks);
          currentModelInput = buildModelInput(features);


          inActivePhase = ExerciseConfig.isInActivePhase(

            exerciseKey: widget.selectedExercise,
            leftKnee: leftKneeAngle,
            rightKnee: rightKneeAngle,
            leftElbow: leftElbowAngle,
            rightElbow: rightElbowAngle,

          );

          if (!inActivePhase) 
          {

            predictionLabel = _text('move_now');
            predictionScore = 0;
            currentTip = ExerciseConfig.idleMessage(
              widget.selectedExercise,
              widget.language,

            );

            predictionHistory.clear();
            _speakIfNeeded(

              isCorrect: false,
              bodyVisible: true,
              tip: currentTip,
              inActivePhase: false,
            );

          } else if (scalerMean.isNotEmpty && mlpLayers.isNotEmpty) 
          {
            final normalizedInput = normalizeInput(currentModelInput);
            final rawPrediction = runMlpPrediction(normalizedInput);



            if (kDebugMode) 
            {

              debugPrint('EXERCISE: ${widget.selectedExercise}');
              debugPrint('RAW PREDICTION: $rawPrediction');

            }

            predictionHistory.add(rawPrediction);


            if (predictionHistory.length > predictionWindowSize) 
            {
              predictionHistory.removeAt(0);
            }



            modelScore = predictionHistory.reduce((a, b) => a + b) /
                predictionHistory.length;



            ruleScore = ExerciseConfig.ruleBasedQuality(

              exerciseKey: widget.selectedExercise,
              leftKnee: leftKneeAngle,
              rightKnee: rightKneeAngle,
              leftElbow: leftElbowAngle,
              rightElbow: rightElbowAngle,

            );

            // ML + kural hibrit skoru: yanlış formları daha iyi yakalar.
            predictionScore = (modelScore * 0.7) + (ruleScore * 0.3);



            final threshold =
                ExerciseConfig.strictThreshold(widget.selectedExercise);
            final isCorrect = predictionScore >= threshold;



            predictionLabel = isCorrect ? 'DOĞRU FORM' : 'YANLIŞ FORM';
            predictionLabel = isCorrect
                ? _text('correct_form')
                : _text('incorrect_form');



            currentTip = ExerciseConfig.formTip(
              exerciseKey: widget.selectedExercise,
              language: widget.language,
              leftKnee: leftKneeAngle,
              rightKnee: rightKneeAngle,
              leftElbow: leftElbowAngle,
              rightElbow: rightElbowAngle,
              isCorrect: isCorrect,
            );



            analyzedFrames++;
            if (isCorrect) correctFrames++;


            if (ExerciseConfig.supportsRepCount(widget.selectedExercise)) 
            {

              updateRepCount();
            }


            _speakIfNeeded(

              isCorrect: isCorrect,
              bodyVisible: true,
              tip: currentTip,
              inActivePhase: true,

            );

          }
        } 
        else {

          predictionLabel = _text('show_full_body');
          predictionScore = 0;
          modelScore = 0;
          ruleScore = 0;
          currentModelInput = [];
          currentTip = null;
          inActivePhase = false;
          predictionHistory.clear();

        }
      });

    });

  }

  Future<void> _initTts() async 
  {

    final tts = FlutterTts();
    await tts.setLanguage(widget.language.ttsCode);
    await tts.setSpeechRate(0.48);
    await tts.setVolume(1.0);
    _tts = tts;

  }

  void _speakIfNeeded(
    {

    required bool isCorrect,
    required bool bodyVisible,
    required bool inActivePhase,
    String? tip,
  }) 
  {
    final message = ExerciseConfig.voiceMessage(

      language: widget.language,
      isCorrect: isCorrect,
      tip: tip,
      bodyVisible: bodyVisible,
      inActivePhase: inActivePhase,

    );


    final now = DateTime.now();
    if (_lastSpokenText == message &&
        _lastSpeakTime != null &&
        now.difference(_lastSpeakTime!) < const Duration(seconds: 4)) 
        {
      return;

    }

    _lastSpokenText = message;
    _lastSpeakTime = now;
    _tts?.speak(message);

  }


  void updateRepCount() 
  {

    final avgKnee = (leftKneeAngle + rightKneeAngle) / 2;
    if (!repWasDown && avgKnee < 100) {

      repWasDown = true;

    }
    if (repWasDown && avgKnee > 155) {

      repWasDown = false;
      repCount++;

    }
  }

  Future<void> loadModelFiles() async 
  {

    try {

      final scalerJson =
          await rootBundle.loadString('assets/models/scaler_params.json');
      final modelJson =
          await rootBundle.loadString('assets/models/mlp_model.json');

      final scalerData = jsonDecode(scalerJson);

      scalerMean = List<double>.from(

        scalerData['mean'].map((value) => value.toDouble()),

      );

      scalerScale = List<double>.from(

        scalerData['scale'].map((value) => value.toDouble()),

      );

      mlpLayers = jsonDecode(modelJson);


      setState(() {

        predictionLabel = _text('ready_start');

      });
    } catch (e) {

      setState(() {

        predictionLabel = _text('model_load_failed');
      });

    }

  }


  void finishSession() {

    if (sessionFinished)
     return;
    sessionFinished = true;

    poseSubscription?.cancel();

    final stats = SessionStats(

      exerciseName: ExerciseConfig.displayName(

        widget.selectedExercise,
        widget.language,
      ),

      exerciseKey: widget.selectedExercise,
      duration: DateTime.now().difference(sessionStart),
      reps: repCount,
      analyzedFrames: analyzedFrames,
      correctFrames: correctFrames,

    );


    Navigator.of(context).pushReplacement(

      MaterialPageRoute(

        builder: (_) => SessionSummaryPage(
          stats: stats,
          language: widget.language,


        ),
      ),

    );

  }

  String _text(String key) {

    final tr = widget.language == AppLanguage.tr;
    switch (key) {

      case 'model_loading':
        return tr ? 'Model yükleniyor...' : 'Loading model...';

      case 'move_now':
        return tr ? 'HAREKETE GEÇİN' : 'START MOVING';

      case 'correct_form':
        return tr ? 'DOĞRU FORM' : 'CORRECT FORM';

      case 'incorrect_form':
        return tr ? 'YANLIŞ FORM' : 'INCORRECT FORM';

      case 'show_full_body':
        return tr ? 'TÜM VÜCUT GÖRÜNSÜN' : 'SHOW FULL BODY';

      case 'ready_start':
        return tr ? 'Hazır — egzersize başlayın' : 'Ready — start exercise';

      case 'model_load_failed':
        return tr ? 'Model yüklenemedi' : 'Model failed to load';

      case 'left_elbow':
        return tr ? 'Sol dirsek' : 'Left elbow';

      case 'right_elbow':
        return tr ? 'Sağ dirsek' : 'Right elbow';

      case 'left_knee':
        return tr ? 'Sol diz' : 'Left knee';

      case 'right_knee':
        return tr ? 'Sağ diz' : 'Right knee';

      case 'finish':
        return tr ? 'Bitir' : 'Finish';

      case 'score':
        return tr ? 'Skor' : 'Score';

      case 'reps':
        return tr ? 'Tekrar' : 'Reps';

      case 'target':
        return tr ? 'Hedef' : 'Target';

      default:
        return key;

    }

  }


  bool isFullBodyVisible(List<PoseLandmarkPoint> points) {

    if (points.length < 33) 
    return false;


    const requiredIndexes = [11, 12, 23, 24, 25, 26, 27, 28];


    for (final index in requiredIndexes) {

      if (points[index].visibility < 0.5) {

        return false;

      }

    }

    return true;

  }

  double calculateAngle(

    PoseLandmarkPoint a,
    PoseLandmarkPoint b,
    PoseLandmarkPoint c,
  ) 
  {

    final abx = a.x - b.x;
    final aby = a.y - b.y;
    final cbx = c.x - b.x;
    final cby = c.y - b.y;


    final dot = (abx * cbx) + (aby * cby);
    final magAB = sqrt((abx * abx) + (aby * aby));
    final magCB = sqrt((cbx * cbx) + (cby * cby));


    if (magAB == 0 || magCB == 0) return 0;


    final cosine = dot / (magAB * magCB);
    final angle = acos(cosine.clamp(-1.0, 1.0));


    return angle * 180 / pi;

  }

  double calculateDistance(PoseLandmarkPoint a, PoseLandmarkPoint b) {

    final dx = a.x - b.x;

    final dy = a.y - b.y;
    return sqrt((dx * dx) + (dy * dy));

  }

  bool isVisible(PoseLandmarkPoint p) {

    return p.visibility > 0.5;

  }


  void calculateExerciseAngles(List<PoseLandmarkPoint> points) {

    if (points.length < 33) 
    return;


    final leftHip = points[23];
    final leftKnee = points[25];
    final leftAnkle = points[27];


    final rightHip = points[24];
    final rightKnee = points[26];
    final rightAnkle = points[28];


    final leftShoulder = points[11];
    final leftElbow = points[13];
    final leftWrist = points[15];


    final rightShoulder = points[12];
    final rightElbow = points[14];
    final rightWrist = points[16];


    if (isVisible(leftHip) && isVisible(leftKnee) && isVisible(leftAnkle)) {

      final newLeftAngle = calculateAngle(leftHip, leftKnee, leftAnkle);
      leftKneeAngle = (leftKneeAngle * (1 - smoothingFactor)) +
          (newLeftAngle * smoothingFactor);

    }

    if (isVisible(rightHip) && isVisible(rightKnee) && isVisible(rightAnkle)) {

      final newRightAngle = calculateAngle(rightHip, rightKnee, rightAnkle);
      rightKneeAngle = (rightKneeAngle * (1 - smoothingFactor)) +
          (newRightAngle * smoothingFactor);

    }

    if (isVisible(leftShoulder) &&
        isVisible(leftElbow) &&
        isVisible(leftWrist)) {
      final newLeftElbow =

          calculateAngle(leftShoulder, leftElbow, leftWrist);
      leftElbowAngle = (leftElbowAngle * (1 - smoothingFactor)) +
          (newLeftElbow * smoothingFactor);

    }

    if (isVisible(rightShoulder) &&
        isVisible(rightElbow) &&
        isVisible(rightWrist)) {

      final newRightElbow =
          calculateAngle(rightShoulder, rightElbow, rightWrist);
      rightElbowAngle = (rightElbowAngle * (1 - smoothingFactor)) +
          (newRightElbow * smoothingFactor);
    }

  }


  Map<String, double> extractFeatures(List<PoseLandmarkPoint> points) {

    final features = <String, double>{};




    // Eğitimdeki frame ortalaması → normalize sonrası ~0 (train/serve uyumu)
    features['frame'] = scalerMean.isNotEmpty ? scalerMean[0] : 0;


    features['left_shoulder_left_hip_left_knee_angle'] =
        calculateAngle(points[11], points[23], points[25]);

    features['right_shoulder_right_hip_right_knee_angle'] =
        calculateAngle(points[12], points[24], points[26]);

    features['left_hip_left_knee_left_ankle_angle'] =
        calculateAngle(points[23], points[25], points[27]);

    features['right_hip_right_knee_right_ankle_angle'] =
        calculateAngle(points[24], points[26], points[28]);

    features['left_shoulder_left_hip_left_ankle_angle'] =
        calculateAngle(points[11], points[23], points[27]);

    features['right_shoulder_right_hip_right_ankle_angle'] =
        calculateAngle(points[12], points[24], points[28]);


    features['shoulder_width'] = calculateDistance(points[11], points[12]);

    features['hip_width'] = calculateDistance(points[23], points[24]);

    features['body_height'] = calculateDistance(points[0], points[27]);



    features['shoulder_hip_ratio'] = features['hip_width'] == 0
        ? 0
        : features['shoulder_width']! / features['hip_width']!;


    features['left_shoulder_left_elbow_left_wrist_angle'] =
        calculateAngle(points[11], points[13], points[15]);

    features['right_shoulder_right_elbow_right_wrist_angle'] =
        calculateAngle(points[12], points[14], points[16]);

    features['left_hip_left_knee_right_knee_angle'] =
        calculateAngle(points[23], points[25], points[26]);

    features['right_hip_right_knee_left_knee_angle'] =
        calculateAngle(points[24], points[26], points[25]);


    features['exercise_type_bridge'] =
        widget.selectedExercise == 'bridge' ? 1 : 0;

    features['exercise_type_knee_pushup'] =
        widget.selectedExercise == 'knee_pushup' ? 1 : 0;

    features['exercise_type_lunge'] =
        widget.selectedExercise == 'lunge' ? 1 : 0;

    features['exercise_type_squat'] =
        widget.selectedExercise == 'squat' ? 1 : 0;


    return features;
  }

  List<double> buildModelInput(Map<String, double> features) {

    const featureColumns = [

      'frame',
      'left_shoulder_left_hip_left_knee_angle',
      'right_shoulder_right_hip_right_knee_angle',
      'left_hip_left_knee_left_ankle_angle',
      'right_hip_right_knee_right_ankle_angle',
      'left_shoulder_left_hip_left_ankle_angle',
      'right_shoulder_right_hip_right_ankle_angle',
      'shoulder_width',
      'hip_width',
      'body_height',
      'shoulder_hip_ratio',
      'left_shoulder_left_elbow_left_wrist_angle',
      'right_shoulder_right_elbow_right_wrist_angle',
      'left_hip_left_knee_right_knee_angle',
      'right_hip_right_knee_left_knee_angle',
      'exercise_type_bridge',
      'exercise_type_knee_pushup',
      'exercise_type_lunge',
      'exercise_type_squat',


    ];

    return featureColumns.map((col) => features[col] ?? 0).toList();

  }

  List<double> normalizeInput(List<double> input) {

    final normalized = <double>[];


    for (int i = 0; i < input.length; i++) {
      final scale = scalerScale[i] == 0 ? 1 : scalerScale[i];
      normalized.add((input[i] - scalerMean[i]) / scale);

    }


    return normalized;

  }

  double relu(double x) => x > 0 ? x : 0;


  double sigmoid(double x) => 1 / (1 + exp(-x));


  List<double> denseLayer(

    List<double> input,
    List<dynamic> weights,
    List<dynamic> bias,
    String activation,

  ) {

    final outputSize = bias.length;
    final output = List<double>.filled(outputSize, 0);



    for (int j = 0; j < outputSize; j++) {

      double sum = bias[j].toDouble();


      for (int i = 0; i < input.length; i++) {

        sum += input[i] * weights[i][j].toDouble();

      }

      if (activation == 'relu') {

        output[j] = relu(sum);

      } 
      else if (activation == 'sigmoid') {

        output[j] = sigmoid(sum);
      } 
      else {

        output[j] = sum;

      }

    }

    return output;

  }

  double runMlpPrediction(List<double> input) {

    List<double> current = input;

    for (final layer in mlpLayers) {

      current = denseLayer(

        current,
        layer['weights'],
        layer['bias'],
        layer['activation'],

      );

    }

    return current.isNotEmpty ? current.first : 0;

  }

  String _primaryAngleLabel() {

    final target = ExerciseConfig.angleTarget(

      widget.selectedExercise,
      widget.language,
    );

    if (target?.trackElbow == true) {

      return '${_text('left_elbow')}: ${leftElbowAngle.toStringAsFixed(1)}°\n'
          '${_text('right_elbow')}: ${rightElbowAngle.toStringAsFixed(1)}°';

    }

    return '${_text('left_knee')}: ${leftKneeAngle.toStringAsFixed(1)}°\n'
        '${_text('right_knee')}: ${rightKneeAngle.toStringAsFixed(1)}°';

  }

  @override
  void dispose() {

    poseSubscription?.cancel();
    _tts?.stop();
    super.dispose();

  }

  @override
  Widget build(BuildContext context) {

    final threshold =
        ExerciseConfig.strictThreshold(widget.selectedExercise);

    final isCorrect =
        inActivePhase && predictionScore >= threshold;


    final angleTarget = ExerciseConfig.angleTarget(
      widget.selectedExercise,
      widget.language,

    );

    final showReps = ExerciseConfig.supportsRepCount(widget.selectedExercise);

    final borderColor = !inActivePhase
        ? Colors.amberAccent
        : (isCorrect ? Colors.greenAccent : Colors.redAccent);

    final labelColor = !inActivePhase
        ? Colors.amberAccent
        : (isCorrect ? Colors.greenAccent : Colors.redAccent);

    return PopScope(

      canPop: false,
      onPopInvokedWithResult: (didPop, result) {

        if (!didPop) finishSession();
      },

      child: Scaffold(

        backgroundColor: Colors.black,
        appBar: AppBar(

          title: Text(

            ExerciseConfig.displayName(widget.selectedExercise, widget.language),

          ),
          backgroundColor: Colors.black,
          foregroundColor: Colors.greenAccent,
          leading: IconButton(

            icon: const Icon(Icons.close),
            onPressed: finishSession,

          ),


          actions: [
            TextButton(
              onPressed: finishSession,
              child: Text(
                _text('finish'),
                style: const TextStyle(color: Colors.greenAccent),
              ),

            ),

          ],

        ),

        body: Stack(


          fit: StackFit.expand,
          children: [


            const NativeCameraPreview(),
            CustomPaint(

              painter: TargetGuidePainter(
                landmarks: landmarks,
                target: angleTarget,
                leftKneeAngle: leftKneeAngle,
                rightKneeAngle: rightKneeAngle,
                leftElbowAngle: leftElbowAngle,
                rightElbowAngle: rightElbowAngle,

              ),

            ),

            CustomPaint(

              painter: LandmarkPainter(landmarks),

            ),

            Positioned(

              top: 12,
              left: 16,
              right: 16,
              child: Container(

                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.65),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: borderColor, width: 2),

                ),
                child: Column(

                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [

                    Text(
                      predictionLabel,
                      style: TextStyle(
                        color: labelColor,
                        fontSize: 22,
                        fontWeight: FontWeight.bold,

                      ),
                    ),

                    if (inActivePhase)
                      Text(
                        '${_text('score')}: ${predictionScore.toStringAsFixed(2)}',
                        style: const TextStyle(color: Colors.white, fontSize: 14),
                      ),

                    if (inActivePhase)
                      Text(
                        'ML: ${modelScore.toStringAsFixed(2)} | Rule: ${ruleScore.toStringAsFixed(2)}',
                        style: const TextStyle(color: Colors.white70, fontSize: 12),
                      ),

                    if (showReps) ...[
                      const SizedBox(height: 4),
                      Text(
                        '${_text('reps')}: $repCount',
                        style: const TextStyle(
                          color: Colors.greenAccent,
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),

                      ),

                    ],

                    if (angleTarget != null) ...[

                      const SizedBox(height: 4),
                      Text(
                        '${_text('target')} ${angleTarget.label}: '
                        '${angleTarget.minAngle.toStringAsFixed(0)}°–'
                        '${angleTarget.maxAngle.toStringAsFixed(0)}°',
                        style: const TextStyle(

                          color: Colors.amberAccent,
                          fontSize: 13,
                        ),

                      ),
                    ],


                    const SizedBox(height: 6),

                    Text(
                      _primaryAngleLabel(),
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                    ),

                    if (currentTip != null) ...[

                      const SizedBox(height: 8),
                      Text(

                        currentTip!,
                        style: const TextStyle(
                          color: Colors.orangeAccent,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),

                      ),

                    ],
                  ],

                ),

              ),
            ),

          ],

        ),
      ),

    );
  }

}


class NativeCameraPreview extends StatelessWidget {

  const NativeCameraPreview({super.key});


  @override
  Widget build(BuildContext context) {

    switch (defaultTargetPlatform) {

      case TargetPlatform.android:
        return const AndroidView(

          viewType: 'camera_preview_view',
          layoutDirection: TextDirection.ltr,

        );
      case TargetPlatform.iOS:
        return const UiKitView(

          viewType: 'camera_preview_view',
          layoutDirection: TextDirection.ltr,

        );

      default:
        return const Center(child: Text('Only Android/iOS supported'));

    }

  }

}

/// Hedef açı aralığını eklem (diz veya dirsek) üzerinde gösterir.
class TargetGuidePainter extends CustomPainter {

  final List<PoseLandmarkPoint> landmarks;
  final AngleTarget? target;
  final double leftKneeAngle;
  final double rightKneeAngle;
  final double leftElbowAngle;
  final double rightElbowAngle;

  TargetGuidePainter({

    required this.landmarks,
    required this.target,
    required this.leftKneeAngle,
    required this.rightKneeAngle,
    required this.leftElbowAngle,
    required this.rightElbowAngle,

  });

  @override
  void paint(Canvas canvas, Size size) {

    if (landmarks.length < 33 || target == null) 

    return;

    if (target!.trackElbow) {

      _drawJointGuide(canvas, size, 11, 13, 15, leftElbowAngle);
      _drawJointGuide(canvas, size, 12, 14, 16, rightElbowAngle);
    } 
    else {

      _drawJointGuide(canvas, size, 23, 25, 27, leftKneeAngle);
      _drawJointGuide(canvas, size, 24, 26, 28, rightKneeAngle);


    }
  }


  void _drawJointGuide(

    Canvas canvas,
    Size size,
    int proximalIdx,
    int jointIdx,
    int distalIdx,
    double currentAngle,

  ) {

    final proximal = landmarks[proximalIdx];
    final joint = landmarks[jointIdx];
    final distal = landmarks[distalIdx];


    if (proximal.visibility < 0.5 ||
        joint.visibility < 0.5 ||
        distal.visibility < 0.5) {

      return;
    }

    final jx = joint.x * size.width;
    final jy = joint.y * size.height;
    final px = proximal.x * size.width;
    final py = proximal.y * size.height;
    final dx = distal.x * size.width;
    final dy = distal.y * size.height;


    const guideLen = 48.0;
    final toProximal = atan2(py - jy, px - jx);

    final inRange = currentAngle >= target!.minAngle &&
        currentAngle <= target!.maxAngle;


    final arcPaint = Paint()
      ..color = (inRange ? Colors.greenAccent : Colors.amberAccent)
          .withValues(alpha: 0.35)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;



    final minRad = target!.minAngle * pi / 180;
    final maxRad = target!.maxAngle * pi / 180;
    final sweep = (maxRad - minRad).clamp(0.05, pi);




    final rect = Rect.fromCircle(center: Offset(jx, jy), radius: guideLen);
    final startAngle = toProximal + pi - maxRad;
    canvas.drawArc(rect, startAngle, sweep, false, arcPaint);



    final boundaryPaint = Paint()
      ..color = Colors.greenAccent.withValues(alpha: 0.55)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;




    for (final angleDeg in [target!.minAngle, target!.maxAngle]) {

      final angleRad = angleDeg * pi / 180;
      final dir = toProximal + pi - angleRad;
      final endX = jx + cos(dir) * guideLen;
      final endY = jy + sin(dir) * guideLen;
      canvas.drawLine(Offset(jx, jy), Offset(endX, endY), boundaryPaint);


    }

    final currentPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.5)
      ..strokeWidth = 2;
    canvas.drawLine(Offset(jx, jy), Offset(dx, dy), currentPaint);


  }

  @override
  bool shouldRepaint(covariant TargetGuidePainter oldDelegate) {


    return oldDelegate.landmarks != landmarks ||
        oldDelegate.leftKneeAngle != leftKneeAngle ||
        oldDelegate.rightKneeAngle != rightKneeAngle ||
        oldDelegate.leftElbowAngle != leftElbowAngle ||
        oldDelegate.rightElbowAngle != rightElbowAngle;


  }


}

class LandmarkPainter extends CustomPainter {


  final List<PoseLandmarkPoint> landmarks;

  LandmarkPainter(this.landmarks);




  static const List<List<int>> connections = [
    [0, 1], [1, 2], [2, 3], [3, 7],
    [0, 4], [4, 5], [5, 6], [6, 8],
    [9, 10],
    [11, 12],
    [11, 13], [13, 15],
    [12, 14], [14, 16],
    [11, 23], [12, 24],
    [23, 24],
    [23, 25], [25, 27],
    [24, 26], [26, 28],
    [27, 29], [29, 31],
    [28, 30], [30, 32],
    [15, 17], [17, 19], [19, 21],
    [16, 18], [18, 20], [20, 22],
  ];




  @override
  void paint(Canvas canvas, Size size) {

    if (landmarks.isEmpty) 
    return;



    final linePaint = Paint()
      ..color = Colors.greenAccent
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke;



    final pointPaint = Paint()
      ..color = Colors.redAccent
      ..style = PaintingStyle.fill;



    for (final pair in connections) {

      final startIndex = pair[0];
      final endIndex = pair[1];

      if (startIndex >= landmarks.length || endIndex >= landmarks.length) {

        continue;

      }



      final start = landmarks[startIndex];
      final end = landmarks[endIndex];



      canvas.drawLine(
        Offset(start.x * size.width, start.y * size.height),
        Offset(end.x * size.width, end.y * size.height),
        linePaint,
      );


    }



    for (final lm in landmarks) {



      canvas.drawCircle(
        Offset(lm.x * size.width, lm.y * size.height),
        5,
        pointPaint,
      );

    }

  }

  @override
  bool shouldRepaint(covariant LandmarkPainter oldDelegate) {

    return oldDelegate.landmarks != landmarks;


  }

  
}

