# modules/data_collector.py

import cv2
import mediapipe as mp
import numpy as np
import csv
import os
from datetime import datetime
from config import Config


class DataCollector:
    def __init__(self):
        """Veri toplama modülünü başlat"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE
        )

        self.mp_drawing = mp.solutions.drawing_utils
        self.landmark_names = [landmark.name.lower() for landmark in self.mp_pose.PoseLandmark]

    def extract_landmarks(self, image):
        """
        Görüntüden landmark noktalarını çıkarır.

        Args:
            image: BGR formatında görüntü

        Returns:
            landmarks: 33x4 numpy array (x, y, z, visibility)
            results: MediaPipe sonuç nesnesi
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        if not results.pose_landmarks:
            return None, results

        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.append([lm.x, lm.y, lm.z, lm.visibility])

        return np.array(landmarks), results

    def collect_from_video(self, video_path, exercise_type, form_label, output_dir="data/raw"):
        """
        Videodan landmark verilerini toplar ve CSV'ye kaydeder.

        Args:
            video_path: Video dosyasının yolu
            exercise_type: Egzersiz tipi
            form_label: Form etiketi (1: doğru, 0: yanlış)
            output_dir: Çıktı dizini
        """
        if exercise_type not in Config.EXERCISE_TYPES:
            raise ValueError(f"Geçersiz egzersiz tipi: {exercise_type}")

        if form_label not in [0, 1]:
            raise ValueError("form_label sadece 0 veya 1 olmalıdır. 1: doğru, 0: yanlış")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video dosyası bulunamadı: {video_path}")

        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Video açılamadı: {video_path}")

        data = []

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            output_dir,
            f"{exercise_type}_{form_label}_{timestamp}.csv"
        )

        frame_count = 0
        saved_frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            landmarks, _ = self.extract_landmarks(frame)

            if landmarks is not None:
                frame_data = [frame_count, exercise_type, form_label]
                frame_data.extend(landmarks.flatten().tolist())
                data.append(frame_data)
                saved_frame_count += 1

            frame_count += 1

            if frame_count % 100 == 0:
                print(f"{frame_count} frame işlendi, {saved_frame_count} frame kaydedildi...")

        cap.release()

        self.save_to_csv(data, output_file)

        print(f"Veri kaydedildi: {output_file}")
        print(f"Toplam işlenen frame: {frame_count}")
        print(f"Kaydedilen landmark frame sayısı: {saved_frame_count}")

        return data

    def collect_from_webcam(self, exercise_type, form_label, duration_seconds=10, output_dir="data/raw"):
        """
        Webcam'den canlı veri toplar.

        Args:
            exercise_type: Egzersiz tipi
            form_label: Form etiketi (1: doğru, 0: yanlış)
            duration_seconds: Toplama süresi
            output_dir: Çıktı dizini
        """
        if exercise_type not in Config.EXERCISE_TYPES:
            raise ValueError(f"Geçersiz egzersiz tipi: {exercise_type}")

        if form_label not in [0, 1]:
            raise ValueError("form_label sadece 0 veya 1 olmalıdır. 1: doğru, 0: yanlış")

        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Webcam açılamadı!")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)

        data = []

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps is None or fps <= 0:
            fps = Config.FPS_TARGET

        max_frames = int(fps * duration_seconds)

        print(f"Veri toplama başlıyor... Süre: {duration_seconds} saniye")
        print(f"Egzersiz tipi: {exercise_type}")
        print(f"Form etiketi: {form_label} {'Doğru' if form_label == 1 else 'Yanlış'}")
        print("Çıkmak için q tuşuna basabilirsiniz.")

        frame_count = 0
        saved_frame_count = 0

        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                print("Frame alınamadı.")
                break

            landmarks, results = self.extract_landmarks(frame)

            if results and results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )

            remaining = max(0, duration_seconds - (frame_count / fps))

            cv2.putText(
                frame,
                f"Kalan: {remaining:.1f}s",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Kaydedilen: {saved_frame_count}",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Label: {'Correct' if form_label == 1 else 'Incorrect'}",
                (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.imshow("Veri Toplama", frame)

            if landmarks is not None:
                frame_data = [frame_count, exercise_type, form_label]
                frame_data.extend(landmarks.flatten().tolist())
                data.append(frame_data)
                saved_frame_count += 1

            frame_count += 1

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            output_dir,
            f"{exercise_type}_{form_label}_live_{timestamp}.csv"
        )

        self.save_to_csv(data, output_file)

        print(f"Veri kaydedildi: {output_file}")
        print(f"Toplam işlenen frame: {frame_count}")
        print(f"Kaydedilen landmark frame sayısı: {saved_frame_count}")

        return data

    def save_to_csv(self, data, output_file):
        """Veriyi CSV formatında kaydeder."""
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        header = ["frame", "exercise_type", "form_label"]

        for name in self.landmark_names:
            for axis in ["x", "y", "z", "vis"]:
                header.append(f"{name}_{axis}")

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)

    def __del__(self):
        """Temizlik işlemleri"""
        if hasattr(self, "pose"):
            self.pose.close()