# config.py

class Config:
    # MediaPipe ayarları
    MIN_DETECTION_CONFIDENCE = 0.5
    MIN_TRACKING_CONFIDENCE = 0.5
    
    # Egzersiz tipleri
    EXERCISE_TYPES = ['squat', 'pushup', 'shoulder_press']
    
    # Landmark indeksleri (MediaPipe Pose Landmarks)
    LANDMARKS = {
        'nose': 0,
        'left_eye_inner': 1,
        'left_eye': 2,
        'left_eye_outer': 3,
        'right_eye_inner': 4,
        'right_eye': 5,
        'right_eye_outer': 6,
        'left_ear': 7,
        'right_ear': 8,
        'mouth_left': 9,
        'mouth_right': 10,
        'left_shoulder': 11,
        'right_shoulder': 12,
        'left_elbow': 13,
        'right_elbow': 14,
        'left_wrist': 15,
        'right_wrist': 16,
        'left_pinky': 17,
        'right_pinky': 18,
        'left_index': 19,
        'right_index': 20,
        'left_thumb': 21,
        'right_thumb': 22,
        'left_hip': 23,
        'right_hip': 24,
        'left_knee': 25,
        'right_knee': 26,
        'left_ankle': 27,
        'right_ankle': 28,
        'left_heel': 29,
        'right_heel': 30,
        'left_foot_index': 31,
        'right_foot_index': 32
    }
    
    # Her egzersiz için kritik açı çiftleri
    EXERCISE_ANGLES = {
        'squat': [
            ('left_hip', 'left_knee', 'left_ankle'),
            ('right_hip', 'right_knee', 'right_ankle'),
            ('left_shoulder', 'left_hip', 'left_knee'),
            ('right_shoulder', 'right_hip', 'right_knee')
        ],
        'pushup': [
            ('left_shoulder', 'left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow', 'right_wrist'),
            ('left_hip', 'left_knee', 'left_ankle'),
            ('right_hip', 'right_knee', 'right_ankle')
        ],
        'shoulder_press': [
            ('left_elbow', 'left_shoulder', 'left_hip'),
            ('right_elbow', 'right_shoulder', 'right_hip'),
            ('left_wrist', 'left_elbow', 'left_shoulder'),
            ('right_wrist', 'right_elbow', 'right_shoulder')
        ]
    }
    
    # Model eğitimi ayarları
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    N_ESTIMATORS = 100
    MAX_DEPTH = 10
    
    # Görüntü ayarları
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS_TARGET = 30
    
    # Renkler (BGR formatında)
    COLORS = {
        'GREEN': (0, 255, 0),
        'RED': (0, 0, 255),
        'BLUE': (255, 0, 0),
        'YELLOW': (0, 255, 255),
        'WHITE': (255, 255, 255),
        'BLACK': (0, 0, 0)
    }