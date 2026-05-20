# utils/angle_utils.py

import numpy as np
import math

def calculate_angle(a, b, c):
    """
    3 nokta arasındaki açıyı hesaplar
    a, b, c: (x, y, z, visibility) formatında landmark noktaları
    """
    # Görünürlük kontrolü
    if a[3] < 0.5 or b[3] < 0.5 or c[3] < 0.5:
        return None
    
    # Sadece x,y koordinatlarını al (2D açı)
    a = np.array([a[0], a[1]])
    b = np.array([b[0], b[1]])
    c = np.array([c[0], c[1]])
    
    # Vektörleri hesapla
    ba = a - b
    bc = c - b
    
    # Kosinüs teoremi ile açı hesapla
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1, 1)  # Numerik hataları önle
    angle = np.arccos(cosine_angle)
    
    return np.degrees(angle)

def calculate_distance(a, b):
    """İki nokta arasındaki mesafeyi hesaplar"""
    if a[3] < 0.5 or b[3] < 0.5:
        return None
    
    return np.linalg.norm([a[0] - b[0], a[1] - b[1], a[2] - b[2]])

def get_body_ratios(landmarks):
    """Vücut oranlarını hesaplar"""
    ratios = {}
    
    # Omuz genişliği / Kalça genişliği oranı
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    
    shoulder_width = calculate_distance(left_shoulder, right_shoulder)
    hip_width = calculate_distance(left_hip, right_hip)
    
    if shoulder_width and hip_width:
        ratios['shoulder_hip_ratio'] = shoulder_width / hip_width
    
    # Kol uzunluğu / Bacak uzunluğu oranı
    left_arm = calculate_distance(landmarks[11], landmarks[15])  # omuz-bilek
    right_arm = calculate_distance(landmarks[12], landmarks[16])
    left_leg = calculate_distance(landmarks[23], landmarks[27])  # kalça-ayak bileği
    right_leg = calculate_distance(landmarks[24], landmarks[28])
    
    if left_arm and left_leg:
        ratios['left_arm_leg_ratio'] = left_arm / left_leg
    if right_arm and right_leg:
        ratios['right_arm_leg_ratio'] = right_arm / right_leg
    
    return ratios