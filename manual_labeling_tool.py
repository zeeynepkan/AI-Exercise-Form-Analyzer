# manual_labeling_tool.py

import cv2
import mediapipe as mp
import numpy as np
import csv
import os
from datetime import datetime
from config import Config

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def extract_landmarks(results):
    if not results.pose_landmarks:
        return None

    landmarks = []
    for lm in results.pose_landmarks.landmark:
        landmarks.append([lm.x, lm.y, lm.z, lm.visibility])

    return np.array(landmarks)


def save_to_csv(data, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    landmark_names = [
        landmark.name.lower()
        for landmark in mp_pose.PoseLandmark
    ]

    header = ["frame", "exercise_type", "form_label"]

    for name in landmark_names:
        for axis in ["x", "y", "z", "vis"]:
            header.append(f"{name}_{axis}")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


def manual_label_video(video_path, exercise_type="lunge"):
    if exercise_type not in Config.EXERCISE_TYPES:
        print(f"Geçersiz egzersiz tipi: {exercise_type}")
        print(f"Geçerli egzersizler: {Config.EXERCISE_TYPES}")
        return

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Video açılamadı: {video_path}")
        return

    pose = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE
    )

    data = []
    frame_count = 0

    print("=" * 60)
    print("MANUEL VIDEO ETIKETLEME")
    print("=" * 60)
    print(f"Video: {video_path}")
    print(f"Egzersiz tipi: {exercise_type}")
    print("=" * 60)
    print("Tuşlar:")
    print("c = correct form")
    print("w = wrong form")
    print("s = skip")
    print("q = çık ve kaydet")
    print("=" * 60)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        display_frame = frame.copy()

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                display_frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        cv2.putText(
            display_frame,
            f"Exercise: {exercise_type}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            display_frame,
            f"Frame: {frame_count}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            display_frame,
            "c: Correct | w: Wrong | s: Skip | q: Quit",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.imshow("Manual Labeling Tool", display_frame)

        key = cv2.waitKey(0) & 0xFF

        if key == ord("q"):
            print("Çıkılıyor ve veri kaydediliyor...")
            break

        elif key == ord("s"):
            print(f"Frame {frame_count}: atlandı")

        elif key == ord("c"):
            landmarks = extract_landmarks(results)

            if landmarks is not None:
                frame_data = [frame_count, exercise_type, 1]
                frame_data.extend(landmarks.flatten().tolist())
                data.append(frame_data)
                print(f"Frame {frame_count}: correct olarak kaydedildi")
            else:
                print(f"Frame {frame_count}: landmark bulunamadı")

        elif key == ord("w"):
            landmarks = extract_landmarks(results)

            if landmarks is not None:
                frame_data = [frame_count, exercise_type, 0]
                frame_data.extend(landmarks.flatten().tolist())
                data.append(frame_data)
                print(f"Frame {frame_count}: wrong olarak kaydedildi")
            else:
                print(f"Frame {frame_count}: landmark bulunamadı")

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
    pose.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/raw/manual_labeled_{exercise_type}_{timestamp}.csv"

    save_to_csv(data, output_file)

    print("=" * 60)
    print(f"Kaydedilen frame sayısı: {len(data)}")
    print(f"Çıktı dosyası: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    video_path = "data/sample_videos/LUNGE_VIDEO.mp4"
    manual_label_video(video_path, exercise_type="lunge")