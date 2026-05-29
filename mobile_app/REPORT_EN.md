# Exercise Form Analyzer - Project Report

## 1. Project Overview
This project is a real-time mobile application that analyzes exercise form using on-device pose estimation and a lightweight neural network. The goal is to help users perform movements more safely by providing instant visual and voice feedback.

## 2. Problem Statement
Many users train without supervision and repeat incorrect movement patterns. This can reduce exercise effectiveness and increase injury risk. The application targets this gap by detecting body landmarks from the camera and classifying movement quality.

## 3. Scope
- Supported exercises: Squat, Lunge, Knee Push-Up, Bridge
- Platforms: Android and iOS
- Input: Live camera stream
- Output:
  - Correct/Incorrect form feedback
  - Exercise-specific tips
  - Voice guidance (TR/EN)
  - Session summary (duration, reps, form accuracy)

## 4. System Architecture
1. Camera stream is processed by MediaPipe pose landmarker.
2. Landmark coordinates are transformed into biomechanical features (angles, distances, ratios).
3. Features are normalized using training scaler parameters.
4. A compact MLP model predicts form quality.
5. A rule-based quality score is combined with ML score for stricter and more stable decisions.
6. UI renders skeleton overlay, target angle guides, and recommendations.

## 5. Data and Features
Feature vector contains:
- Joint angle features (hip-knee-ankle, shoulder-hip-knee, elbow angles)
- Body geometry (shoulder width, hip width, body-height approximation, ratios)
- Exercise one-hot encoding

To reduce train/serve mismatch, the `frame` feature is aligned with scaler mean so normalized value remains consistent.

## 6. Inference Strategy
The final decision uses a hybrid score:
- `modelScore`: smoothed MLP probability (windowed average)
- `ruleScore`: kinematics-based quality score (0..1)
- `finalScore = 0.7 * modelScore + 0.3 * ruleScore`

Exercise-specific strict thresholds are applied to reduce false positives (cases where the app incorrectly says "Correct").

## 7. UX Features
- Full-body visibility check before inference
- Active-phase gating (no evaluation while idle/standing)
- Exercise-specific correction tips
- Voice feedback in Turkish and English
- Persistent language and theme preferences
- Session summary page after workout

## 8. Engineering Decisions
- On-device inference for low latency and privacy
- JSON-exported scaler + MLP for lightweight deployment
- Rule-assisted post-processing to improve practical robustness
- Modular utility layer for language and exercise configuration

## 9. Limitations
- Performance depends on camera angle, lighting, clothing, and occlusion
- Single-person assumption
- Rule thresholds are heuristic and may need per-user calibration
- No long-term cloud analytics in current version

## 10. Future Work
- Personalized threshold tuning based on user profile
- More exercise classes and error categories
- Better temporal modeling (sequence model instead of frame-level MLP)
- Dataset expansion and benchmark reporting (precision/recall/F1)
- Remote coach dashboard and progress tracking

## 11. Conclusion
The project delivers a complete, real-time, privacy-preserving exercise form analyzer on mobile. By combining pose estimation, ML inference, and rule-based correction logic, it provides practical and understandable feedback for safe home training.
