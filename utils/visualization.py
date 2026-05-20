# utils/visualization.py

import cv2
import numpy as np
from config import Config

def draw_landmarks(frame, landmarks, connections=None):
    """Landmark noktalarını ve bağlantılarını çizer"""
    h, w = frame.shape[:2]
    
    # Noktaları çiz
    for idx, lm in enumerate(landmarks):
        if lm[3] > 0.5:  # Görünürlük kontrolü
            cx, cy = int(lm[0] * w), int(lm[1] * h)
            cv2.circle(frame, (cx, cy), 3, Config.COLORS['GREEN'], -1)
    
    # Bağlantıları çiz (MediaPipe Pose connections)
    if connections:
        for connection in connections:
            start_idx, end_idx = connection
            if landmarks[start_idx][3] > 0.5 and landmarks[end_idx][3] > 0.5:
                start_point = (int(landmarks[start_idx][0] * w), 
                              int(landmarks[start_idx][1] * h))
                end_point = (int(landmarks[end_idx][0] * w), 
                            int(landmarks[end_idx][1] * h))
                cv2.line(frame, start_point, end_point, Config.COLORS['BLUE'], 2)
    
    return frame

def draw_info_panel(frame, angles, rep_count, form_status, exercise_type):
    """Bilgi panelini çizer"""
    h, w = frame.shape[:2]
    
    # Arkaplan paneli
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (300, 200), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
    
    # Egzersiz tipi
    cv2.putText(frame, f"Exercise: {exercise_type}", 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, Config.COLORS['WHITE'], 2)
    
    # Tekrar sayısı
    cv2.putText(frame, f"Reps: {rep_count}", 
                (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, Config.COLORS['WHITE'], 2)
    
    # Form durumu
    color = Config.COLORS['GREEN'] if form_status == "Correct" else Config.COLORS['RED']
    cv2.putText(frame, f"Form: {form_status}", 
                (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Açılar
    y_offset = 130
    for angle_name, angle_value in list(angles.items())[:3]:  # İlk 3 açıyı göster
        if angle_value:
            cv2.putText(frame, f"{angle_name}: {angle_value:.1f}", 
                        (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, Config.COLORS['YELLOW'], 1)
            y_offset += 25
    
    return frame

def draw_angle_arc(frame, center, angle, color):
    """Açıyı görselleştirmek için yay çizer"""
    h, w = frame.shape[:2]
    center_point = (int(center[0] * w), int(center[1] * h))
    
    # Yay çiz
    axes = (30, 30)
    start_angle = 0
    end_angle = int(angle)
    cv2.ellipse(frame, center_point, axes, 0, start_angle, end_angle, color, 2)
    
    return frame