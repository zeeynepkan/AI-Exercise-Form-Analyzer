# 🏋️ AI Exercise Form Analyzer

An AI-powered real-time exercise form analysis system that combines Computer Vision, Machine Learning, and Mobile Development to evaluate exercise performance and provide instant feedback to users.

This project was developed as a Graduation Thesis Project at the Department of Computer Engineering, Çukurova University. The system combines computer vision and machine learning techniques to provide real-time exercise form analysis on mobile devices.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![Flutter](https://img.shields.io/badge/Flutter-3.x-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-green)

## 📥 Download APK

👉 [Download Latest APK](https://github.com/zeeynepkan/AI-Exercise-Form-Analyzer/releases/latest)


## ✨ Features

- Real-time exercise form analysis
- Instant visual feedback
- MediaPipe Pose landmark detection
- TensorFlow MLP classifier
- Support for Squat, Lunge, Knee Push-Up and Bridge exercises
- Multi-language support (English / Turkish)
- Dark and Light theme support
- Session statistics tracking
- Mobile deployment with Flutter

## 📱 Application Screenshots
<img width="240" height="500" alt="image" src="https://github.com/user-attachments/assets/25950bd5-0ba1-4a71-b4fc-b62bd06d80d2" />    <img width="240" height="500" alt="image" src="https://github.com/user-attachments/assets/29180b14-a771-4a65-84b7-19fa71752b57" />    <img width="240" height="500" alt="image" src="https://github.com/user-attachments/assets/2a905b98-f8b7-4955-bafe-0368875864db" />

## 🏃 Supported Exercises

| Exercise | Supported |
|-----------|-----------|
| Squat | ✅ |
| Lunge | ✅ |
| Knee Push-Up | ✅ |
| Bridge | ✅ |

## 📊 Dataset

The dataset was created manually using exercise videos and MediaPipe Pose landmarks.

Data collection process:

- Exercise videos were recorded for each exercise type.
- MediaPipe Pose was used to extract body landmarks.
- Frames were manually labeled as correct or incorrect form.
- Angle-based features were extracted from pose landmarks.
- The final dataset was used to train Random Forest and TensorFlow MLP models.

Supported exercises:
- Squat
- Lunge
- Knee Push-Up
- Bridge

## 🤖 Machine Learning Pipeline

```text
Exercise Videos
      ↓
Manual Labeling
      ↓
Feature Extraction
      ↓
Feature Normalization
      ↓
Random Forest / TensorFlow MLP
      ↓
Model Export
      ↓
Flutter Mobile Application
```



## 📦 Deployment

The Android application has been successfully deployed and tested through Google Play Console internal testing.



## 💻 Installation and Setup
1. Clone the Repository 
  ```bash
git clone https://github.com/zeeynepkan/AI-Exercise-Form-Analyzer.git
cd AI-Exercise-Form-Analyzer
```

2. Create a Python Virtual Environment
 ### Windows

```bash
py -m venv venv
venv\Scripts\activate
```
  ### Linux / macOS
```bash
  py -m venv venv
  source venv/bin/activate
```
3. Install Required Python Packages
   
```bash
pip install -r requirements.txt
```

 
4. Train Models

Random Forest:
```bash
py train_model.py
```

TensorFlow MLP:
```bash
py train_tensorflow_model.py
```
Export Mobile Models
```bash
py export_mlp_weights.py
py export_mobile_metadata.py
```
Optional TFLite conversion:
```bash
py convert_to_tflite.py
```

5. Run the Desktop Prototype


Real-time exercise analysis on PC:
```bash
py realtime_ml_analyzer.py
```


## 📱 Flutter Mobile Application Setup

Navigate to the mobile application directory:
```bash
cd mobile_app
flutter pub get
flutter run device-ID
```

Build Android APK
```bash
flutter build apk --release
```

Build Android App Bundle
```bash
flutter build appbundle --release
```

## 📋 Requirements

### Python
- Python 3.12+
- TensorFlow
- MediaPipe
- OpenCV
- Scikit-Learn
- Pandas
- NumPy

### Flutter
- Flutter 3.x
- Dart SDK
- Android Studio
- Android SDK
- 
## 📂 Repository Structure

```text
AI-Exercise-Form-Analyzer
│
├── mobile_app/
├── modules/
├── tests/
├── utils/
├── data/
│   ├── raw/
│   ├── processed/
│   └── models/
│
├── manual_labeling_tool.py
├── train_model.py
├── train_tensorflow_model.py
├── export_mlp_weights.py
├── export_mobile_metadata.py
├── realtime_ml_analyzer.py
└── README.md
```

## 👩‍💻 Author

**Zeynep Kan**

Computer Engineering Student  
Çukurova University

Graduation Thesis Project (2026)

GitHub:
https://github.com/zeeynepkan




