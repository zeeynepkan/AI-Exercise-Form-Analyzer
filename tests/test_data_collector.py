# tests/test_data_collector.py

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_collector import DataCollector


def test_video_collection():
    """Videolardan veri toplamayı test et"""

    collector = DataCollector()

    videos = [
        {
            "path": "data/sample_videos/SQUAT_TRUE.mp4",
            "label": 1
        },
        {
            "path": "data/sample_videos/SQUAT_FALSE.mp4",
            "label": 0
        }
    ]

    for video in videos:

        video_path = video["path"]
        form_label = video["label"]

        if os.path.exists(video_path):

            print(f"\nVideo işleniyor: {video_path}")

            collector.collect_from_video(
                video_path=video_path,
                exercise_type='squat',
                form_label=form_label
            )

        else:
            print(f"Video dosyası bulunamadı: {video_path}")


if __name__ == "__main__":

    print("Veri toplama testi başlıyor...")

    os.makedirs("data/raw", exist_ok=True)

    test_video_collection()

    print("\nTest tamamlandı!")