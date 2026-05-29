# squat_analyzer.py - GERÇEK ZAMANLI SQUAT ANALİZİ  


#başta kullandığım sadece squat için olan analiz
import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):

    """3 nokta arasındaki açıyı hesaplar."""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    ba = a - b
    bc = c - b

    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)



    if norm_ba == 0 or norm_bc == 0:
        return 0

    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))



    return np.degrees(angle)


def is_full_body_visible(landmarks, visibility_threshold=0.25):


    """Squat için en az bir bacak görünür mü kontrol eder."""
    left_side = [
        mp_pose.PoseLandmark.LEFT_HIP.value,
        mp_pose.PoseLandmark.LEFT_KNEE.value,
        mp_pose.PoseLandmark.LEFT_ANKLE.value,
    ]


    right_side = [
        mp_pose.PoseLandmark.RIGHT_HIP.value,
        mp_pose.PoseLandmark.RIGHT_KNEE.value,
        mp_pose.PoseLandmark.RIGHT_ANKLE.value,
    ]


    left_visible = all(landmarks[i].visibility > visibility_threshold for i in left_side)
    right_visible = all(landmarks[i].visibility > visibility_threshold for i in right_side)

    return left_visible or right_visible


def main():

    print("=" * 60)
    print("🏋️ GERÇEK ZAMANLI SQUAT ANALİZİ")
    print("=" * 60)
    print("Kameraya vücudunuz görünecek şekilde durun.")

    print("Çıkmak için 'q' tuşuna basın")
    print("-" * 60)

    window_name = "Squat Analiz Sistemi"



    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    if not cap.isOpened():
        print("Webcam açılamadı!")
        return

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    pose = mp_pose.Pose(

        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )


    rep_count = 0

    is_squatting = False

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Webcam hatası!")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            if not is_full_body_visible(landmarks):
                cv2.putText(


                    frame,
                    "VUCUDUNU BIRAZ DAHA GOSTER!",
                    (80, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )



                cv2.putText(


                    frame,
                    "Squat analizi icin kalca, diz ve ayak bilegi gorunmeli.",
                    (80, 285),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )


            else:
                mp_drawing.draw_landmarks(

                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )


                right_visible = all(

                    landmarks[i].visibility > 0.25
                    for i in [
                        mp_pose.PoseLandmark.RIGHT_HIP.value,
                        mp_pose.PoseLandmark.RIGHT_KNEE.value,
                        mp_pose.PoseLandmark.RIGHT_ANKLE.value,
                    ]
                )


                left_visible = all(

                    landmarks[i].visibility > 0.25
                    for i in [
                        mp_pose.PoseLandmark.LEFT_HIP.value,
                        mp_pose.PoseLandmark.LEFT_KNEE.value,
                        mp_pose.PoseLandmark.LEFT_ANKLE.value,
                    ]
                )


                knee_angles = []


                if right_visible:
                    right_knee = calculate_angle(

                        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
                        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
                    )

                    knee_angles.append(right_knee)
                else:
                    right_knee = None

                if left_visible:
                    left_knee = calculate_angle(

                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
                        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
                    )

                    knee_angles.append(left_knee)
                else:
                    left_knee = None


                avg_knee = sum(knee_angles) / len(knee_angles)


                if avg_knee < 100 and not is_squatting:
                    is_squatting = True
                    print(f"🔽 Squat! Diz açısı: {avg_knee:.1f}°")

                elif avg_knee > 160 and is_squatting:
                    is_squatting = False
                    rep_count += 1
                    print(f"✅ Tekrar {rep_count}! Diz açısı: {avg_knee:.1f}°")



                form_status = "Dogru Form"
                form_color = (0, 255, 0)

                if avg_knee < 90:

                    form_status = "Fazla Asagi!"

                    form_color = (0, 0, 255)

                elif avg_knee > 120 and is_squatting:

                    form_status = "Yeterli Asagi Inmiyorsun!"
                    form_color = (0, 165, 255)


                overlay = frame.copy()

                cv2.rectangle(overlay, (10, 10), (450, 190), (0, 0, 0), -1)
                frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)


                cv2.putText(frame, "SQUAT ANALIZI", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                

                right_text = "-" if right_knee is None else f"{int(right_knee)} derece"
                left_text = "-" if left_knee is None else f"{int(left_knee)} derece"


                cv2.putText(frame, f"Sag Diz: {right_text}", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                

                cv2.putText(frame, f"Sol Diz: {left_text}", (20, 95),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                

                cv2.putText(frame, f"Ortalama: {int(avg_knee)} derece", (20, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)


                cv2.putText(frame, f"Form: {form_status}", (20, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, form_color, 2)
                


                cv2.putText(frame, f"TEKRAR: {rep_count}", (295, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

                if is_squatting:
                    cv2.putText(frame, "SQUAT POZISYONU", (260, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                    

                bar_width = int((avg_knee / 180) * 200)
                cv2.rectangle(frame, (470, 30), (670, 50), (100, 100, 100), -1)

                cv2.rectangle(frame, (470, 30), (470 + bar_width, 50), (0, 255, 0), -1)

                cv2.putText(frame, "Diz Acisi", (470, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                

        else:
            cv2.putText(

                frame,
                "VUCUT TESPIT EDILEMEDI!",
                (150, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )


        cv2.putText(

            frame,
            "Komut: 'q' Cikis",
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )


        cv2.imshow(window_name, frame)



        if cv2.waitKey(1) & 0xFF == ord("q"):
            break



    cap.release()

    cv2.destroyAllWindows()

    pose.close()

    print("\n" + "=" * 60)

    print(f"🏆 PROGRAM SONLANDI - Toplam Tekrar: {rep_count}")
    
    print("=" * 60)




if __name__ == "__main__":
    main()