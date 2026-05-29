# modules/feature_extractor.py

import sys
import os
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from config import Config


class FeatureExtractor:
    def __init__(self):
        self.landmarks = Config.LANDMARKS

    def calculate_angle(self, a, b, c):

        """Belirlenen 3 nokta arasındaki açıyı hesaplar."""
        a = np.array(a[:2])

        b = np.array(b[:2])

        c = np.array(c[:2])

        ba = a - b
        bc = c - b

        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)



        if norm_ba == 0 or norm_bc == 0:
            return 0

        cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)

        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

        return np.degrees(angle)

    def get_landmark_point(self, row, landmark_name):

        """CSV satırından landmark x, y, z, visibility değerlerini alır."""
        return [
            row[f"{landmark_name}_x"],
            row[f"{landmark_name}_y"],
            row[f"{landmark_name}_z"],
            row[f"{landmark_name}_vis"]
        ]

    def extract_angles_from_row(self, row, exercise_type):

        """Bir frame için açı özelliklerini çıkarır."""
        features = {}

        angle_triples = Config.EXERCISE_ANGLES.get(exercise_type, [])

        for point_a, point_b, point_c in angle_triples:

            a = self.get_landmark_point(row, point_a)

            b = self.get_landmark_point(row, point_b)

            c = self.get_landmark_point(row, point_c)

            angle_name = f"{point_a}_{point_b}_{point_c}_angle"

            features[angle_name] = self.calculate_angle(a, b, c)

        return features

    def extract_body_ratios_from_row(self, row):

        """Vücut oranı özellikleri çıkarır."""

        features = {}

        left_shoulder = self.get_landmark_point(row, "left_shoulder")

        right_shoulder = self.get_landmark_point(row, "right_shoulder")

        left_hip = self.get_landmark_point(row, "left_hip")

        right_hip = self.get_landmark_point(row, "right_hip")

        left_ankle = self.get_landmark_point(row, "left_ankle")

        right_ankle = self.get_landmark_point(row, "right_ankle")

        shoulder_width = np.linalg.norm(
            np.array(left_shoulder[:2]) - np.array(right_shoulder[:2])
        )


        hip_width = np.linalg.norm(
            np.array(left_hip[:2]) - np.array(right_hip[:2])
        )


        shoulder_center = (
            np.array(left_shoulder[:2]) + np.array(right_shoulder[:2])
        ) / 2


        ankle_center = (
            np.array(left_ankle[:2]) + np.array(right_ankle[:2])
        ) / 2


        body_height = np.linalg.norm(shoulder_center - ankle_center)


        features["shoulder_width"] = shoulder_width

        features["hip_width"] = hip_width

        features["body_height"] = body_height

        features["shoulder_hip_ratio"] = shoulder_width / hip_width if hip_width != 0 else 0

        return features

    def process_csv(self, input_csv, output_csv="data/processed/features.csv"):

        """Ham landmark CSV dosyasını Machine learning için feature CSV dosyasına çevirir."""


        df = pd.read_csv(input_csv)


        feature_rows = []

        for _, row in df.iterrows():
            exercise_type = row["exercise_type"]

            features = {

                "frame": row["frame"],
                "exercise_type": exercise_type,
                "form_label": row["form_label"]
            }




            angle_features = self.extract_angles_from_row(row, exercise_type)
            ratio_features = self.extract_body_ratios_from_row(row)



            features.update(angle_features)
            features.update(ratio_features)



            feature_rows.append(features)

        feature_df = pd.DataFrame(feature_rows)


        os.makedirs("data/processed", exist_ok=True)
        feature_df.to_csv(output_csv, index=False)



        print(f"Feature dosyası oluşturuldu: {output_csv}")
        print(f"Toplam frame: {len(feature_df)}")
        print(f"Feature sayısı: {len(feature_df.columns) - 3}")


        return feature_df


if __name__ == "__main__":
    extractor = FeatureExtractor()



    raw_files = glob.glob("data/raw/*.csv")



    if not raw_files:
        print("data/raw klasöründe CSV dosyası bulunamadı.")
    else:
        all_features = []




        print("=" * 60)
        print("FEATURE EXTRACTION BASLIYOR")
        print("=" * 60)



        for file_path in raw_files:
            print(f"\nİşleniyor: {file_path}")



            feature_df = extractor.process_csv(
                input_csv=file_path,
                output_csv="data/processed/temp_features.csv"
            )



            all_features.append(feature_df)





        final_df = pd.concat(all_features, ignore_index=True)


        os.makedirs("data/processed", exist_ok=True)



        final_output = "data/processed/features.csv"


        final_df.to_csv(final_output, index=False)

        temp_file = "data/processed/temp_features.csv"


        if os.path.exists(temp_file):
            os.remove(temp_file)



        print("\n" + "=" * 60)
        
        print("TUM FEATURE DOSYALARI BIRLESTIRILDI")
        print(f"Output: {final_output}")
        print(f"Total frame: {len(final_df)}")
        print("Label dagilimi:")
        print(final_df["form_label"].value_counts())
        print("=" * 60)