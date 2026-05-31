#🏋️ AI Exercise Form Analyzer

An AI-powered real-time exercise form analysis system that combines Computer Vision, Machine Learning, and Mobile Development to evaluate exercise performance and provide instant feedback to users.

This project was developed as a Graduation Thesis Project at the Department of Computer Engineering, Çukurova University. The system combines computer vision and machine learning techniques to provide real-time exercise form analysis on mobile devices.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![Flutter](https://img.shields.io/badge/Flutter-3.x-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-green)

## 🚀 Quick Overview

- Real-time exercise form analysis
- MediaPipe Pose landmark detection
- TensorFlow MLP classification
- Flutter mobile application
- Multi-language support
- Dark / Light theme support
- Session statistics tracking


## 📱 Application Screenshots
<img width="240" height="500" alt="image" src="https://github.com/user-attachments/assets/25950bd5-0ba1-4a71-b4fc-b62bd06d80d2" />    <img width="240" height="500" alt="image" src="https://github.com/user-attachments/assets/29180b14-a771-4a65-84b7-19fa71752b57" />    <img width="240" height="500" alt="image" src="https://github.com/user-attachments/assets/2a905b98-f8b7-4955-bafe-0368875864db" />




## 📦 Deployment

The Android application has been successfully deployed and tested through Google Play Console internal testing.



##💻 Installation and Setup
1. Clone the Repository 
   git clone https://github.com/zeeynepkan/AI-Exercise-Form-Analyzer.git
   
   cd AI-Exercise-Form-Analyzer
 2. Create a Python Virtual Environment
    
  Windows

python -m venv venv
venv\Scripts\activate

  Linux / macOS

  python -m venv venv
  
source venv/bin/activate


3. Install Required Python Packages

 pip install tensorflow
 
pip install scikit-learn

pip install mediapipe

pip install opencv-python

pip install pandas

pip install numpy

pip install joblib


4. Run the Desktop Prototype

   

Real-time exercise analysis on PC:


py realtime_ml_analyzer.py


##📱 Flutter Mobile Application Setup

Navigate to the mobile application directory:

cd mobile_app

flutter pub get

flutter run device-ID


