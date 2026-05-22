# realtime_ml_analyzer.py

import warnings
warnings.filterwarnings("ignore")

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import joblib

from modules.feature_extractor import FeatureExtractor

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def landmark_to_dict(landmarks):
    landmark_names = [lm.name.lower() for lm in mp_pose.PoseLandmark]
    data = {}

    for i, lm in enumerate(landmarks):
        name = landmark_names[i]
        data[f"{name}_x"] = lm.x
        data[f"{name}_y"] = lm.y
        data[f"{name}_z"] = lm.z
        data[f"{name}_vis"] = lm.visibility

    return data


def is_squat_body_visible(landmarks, threshold=0.35):
    """Squat analizi için alt vücut yeterince görünüyor mu kontrol eder."""
    required = [
        mp_pose.PoseLandmark.LEFT_HIP.value,
        mp_pose.PoseLandmark.RIGHT_HIP.value,
        mp_pose.PoseLandmark.LEFT_KNEE.value,
        mp_pose.PoseLandmark.RIGHT_KNEE.value,
        mp_pose.PoseLandmark.LEFT_ANKLE.value,
        mp_pose.PoseLandmark.RIGHT_ANKLE.value,
    ]

    visible_count = sum(
        landmarks[i].visibility > threshold
        for i in required
    )

    return visible_count >= 4


def get_average_knee_angle(features):
    """Sol ve sağ diz açılarını kullanarak ortalama diz açısını hesaplar."""
    left_knee = features.get("left_hip_left_knee_left_ankle_angle", None)
    right_knee = features.get("right_hip_right_knee_right_ankle_angle", None)

    angles = []

    if left_knee is not None:
        angles.append(left_knee)

    if right_knee is not None:
        angles.append(right_knee)

    if not angles:
        return 180

    return sum(angles) / len(angles)


def main():

    print("=" * 60)
    print("AI DESTEKLI GERCEK ZAMANLI SQUAT ANALIZI")
    print("=" * 60)

    model_data = joblib.load("data/models/exercise_form_model.pkl")

    model = model_data["model"]
    feature_columns = model_data["feature_columns"]

    extractor = FeatureExtractor()

    pose = mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Webcam açılamadı!")
        return

    rep_count = 0
    is_squatting = False
    correct_frames = 0
    wrong_frames = 0
    confidence_values = []

    window_name = "AI Exercise Form Analysis"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:

            landmarks = results.pose_landmarks.landmark

            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

            if not is_squat_body_visible(landmarks):
                cv2.rectangle(frame, (20, 20), (680, 150), (0, 0, 0), -1)

                cv2.putText(
                    frame,
                    "SQUAT ICIN ALT VUCUDUNU GOSTER!",
                    (40, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    3
                )

                cv2.putText(
                    frame,
                    "Kalca, diz ve ayak bilekleri gorunmeli.",
                    (40, 115),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(window_name, frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                continue

            row_data = landmark_to_dict(landmarks)
            row_data["exercise_type"] = "squat"

            row_series = pd.Series(row_data)

            angle_features = extractor.extract_angles_from_row(
                row_series,
                "squat"
            )

            ratio_features = extractor.extract_body_ratios_from_row(row_series)

            features = {}
            features.update(angle_features)
            features.update(ratio_features)

            avg_knee_angle = get_average_knee_angle(features)

            if avg_knee_angle < 100 and not is_squatting:
                is_squatting = True

            elif avg_knee_angle > 160 and is_squatting:
                is_squatting = False
                rep_count += 1

            feature_df = pd.DataFrame([features])

            for col in feature_columns:
                if col not in feature_df.columns:
                    feature_df[col] = 0

            feature_df = feature_df[feature_columns]

            prediction = model.predict(feature_df)[0]
            probabilities = model.predict_proba(feature_df)[0]
            confidence = np.max(probabilities) * 100

            confidence_values.append(confidence)

            if prediction == 1:
                label = "CORRECT FORM"
                color = (0, 255, 0)
                correct_frames += 1
            else:
                label = "INCORRECT FORM"
                color = (0, 0, 255)
                wrong_frames += 1

            cv2.rectangle(frame, (20, 20), (500, 205), (0, 0, 0), -1)

            cv2.putText(
                frame,
                label,
                (40, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                3
            )

            cv2.putText(
                frame,
                f"Confidence: %{confidence:.1f}",
                (40, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Reps: {rep_count}",
                (40, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Knee Angle: {int(avg_knee_angle)}",
                (40, 185),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

        else:
            cv2.putText(
                frame,
                "VUCUT TESPIT EDILEMEDI!",
                (40, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                3
            )

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    avg_confidence = (
        sum(confidence_values) / len(confidence_values)
        if confidence_values
        else 0
    )

    print("\n" + "=" * 60)
    print("SESSION SUMMARY")
    print("=" * 60)
    print(f"Toplam tekrar: {rep_count}")
    print(f"Correct frame sayisi: {correct_frames}")
    print(f"Wrong frame sayisi: {wrong_frames}")
    print(f"Ortalama confidence: %{avg_confidence:.1f}")
    print("=" * 60)

    cap.release()
    cv2.destroyAllWindows()
    pose.close()


if __name__ == "__main__":
    main()