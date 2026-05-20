# test_system.py

import cv2
import numpy as np
import os
import sys
from datetime import datetime
import mediapipe as mp

# Proje dizinini ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_collector import DataCollector
from utils.angle_utils import calculate_angle, get_body_ratios
from utils.visualization import draw_landmarks, draw_info_panel
from config import Config

def test_1_mediapipe_kurulumu():
    """Test 1: MediaPipe'in düzgün çalıştığını kontrol et"""
    print("\n🔍 Test 1: MediaPipe Kurulumu Kontrolü")
    print("-" * 50)
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe başarıyla import edildi")
        
        # Pose modelini dene
        pose = mp.solutions.pose.Pose()
        print("✅ MediaPipe Pose modeli oluşturuldu")
        
        # Test görüntüsü oluştur
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = pose.process(cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB))
        print("✅ Pose processing çalışıyor")
        
        return True
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def test_2_webcam_acma():
    """Test 2: Webcam'in açılıp açılmadığını kontrol et"""
    print("\n🔍 Test 2: Webcam Kontrolü")
    print("-" * 50)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Webcam açılamadı!")
        return False
    
    print("✅ Webcam başarıyla açıldı")
    
    # Bir frame almayı dene
    ret, frame = cap.read()
    if ret and frame is not None:
        print(f"✅ Frame alındı - Boyut: {frame.shape}")
    else:
        print("❌ Frame alınamadı")
        cap.release()
        return False
    
    cap.release()
    return True

def test_3_landmark_cikarma():
    """Test 3: Landmark çıkarma fonksiyonunu test et"""
    print("\n🔍 Test 3: Landmark Çıkarma")
    print("-" * 50)
    
    collector = DataCollector()
    
    # Test görüntüsü oluştur (basit bir insan silüeti)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Landmark çıkarmayı dene
    landmarks, results = collector.extract_landmarks(test_image)
    
    if landmarks is not None:
        print(f"✅ Landmark çıkarıldı - Shape: {landmarks.shape}")
        print(f"   İlk landmark: {landmarks[0]}")
    else:
        print("ℹ️ Landmark bulunamadı (bu normal, görüntüde insan yok)")
    
    return True

def test_4_aci_hesaplama():
    """Test 4: Açı hesaplama fonksiyonunu test et"""
    print("\n🔍 Test 4: Açı Hesaplama")
    print("-" * 50)
    
    # Test noktaları (x, y, z, visibility)
    # b noktasındaki açının 45° olması için:
    # vektörler: ba = (1,0), bc = (1,1)
    a = [1, 0, 0, 1]    # (1,0)
    b = [0, 0, 0, 1]    # (0,0)
    c = [1, 1, 0, 1]    # (1,1)
    
    angle = calculate_angle(a, b, c)
    expected_angle = 45  # 45 derece olmalı
    
    if angle and abs(angle - expected_angle) < 0.1:
        print(f"✅ Açı hesaplama doğru çalışıyor: {angle:.1f}°")
    else:
        print(f"❌ Açı hesaplama hatası: {angle}°, beklenen: {expected_angle}°")
    
    return True

def test_5_veri_kaydetme():
    """Test 5: Veri kaydetme fonksiyonunu test et"""
    print("\n🔍 Test 5: Veri Kaydetme")
    print("-" * 50)
    
    # Data klasörünü kontrol et
    os.makedirs("data/raw", exist_ok=True)
    print("✅ Data klasörü hazır")
    
    collector = DataCollector()
    
    # Test verisi oluştur
    test_data = [
        [0, 'test', 1] + [0.1] * (33 * 4),  # 33 landmark * 4 değer
        [1, 'test', 1] + [0.2] * (33 * 4)
    ]
    
    # Kaydetmeyi dene
    test_file = "data/raw/test_output.csv"
    collector.save_to_csv(test_data, test_file, 2)
    
    if os.path.exists(test_file):
        print(f"✅ Veri başarıyla kaydedildi: {test_file}")
        print(f"   Dosya boyutu: {os.path.getsize(test_file)} bytes")
    else:
        print("❌ Veri kaydedilemedi")
        return False
    
    return True

def test_6_canli_goruntu():
    """Test 6: Canlı görüntü almayı dene (isteğe bağlı)"""
    print("\n🔍 Test 6: Canlı Görüntü Testi")
    print("-" * 50)
    print("Webcam'den canlı görüntü alınıyor...")
    print("Pencerede 'q' tuşuna basarak çıkabilirsiniz")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    collector = DataCollector()
    frame_count = 0
    start_time = cv2.getTickCount()
    
    # Q'ya basana kadar açık kalsın.
    # (Kameradan döngüye girip pencereyi hemen kapatmamak için 30 frame sınırını kaldırıyoruz.)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Landmark çıkarmayı dene
        landmarks, results = collector.extract_landmarks(frame)
        
        # Görselleştir
        if results and results.pose_landmarks:
            # MediaPipe'in kendi drawing fonksiyonu
            mp.solutions.drawing_utils.draw_landmarks( # type: ignore
                frame, 
                results.pose_landmarks, 
                mp.solutions.pose.POSE_CONNECTIONS # type: ignore
            )
            
            # Landmark sayısını göster
            cv2.putText(frame, f"Landmarks: {len(landmarks) if landmarks is not None else 0}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Test - Canli Goruntu', frame)
        frame_count += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # FPS hesapla
    end_time = cv2.getTickCount()
    fps = frame_count / ((end_time - start_time) / cv2.getTickFrequency())
    print(f"✅ {frame_count} frame işlendi - Ortalama FPS: {fps:.1f}")
    
    return True

def run_all_tests():
    """Tüm testleri çalıştır"""
    print("=" * 60)
    print("🤖 AKILLI EGZERSİZ FORMU ANALİZ SİSTEMİ TESTİ")
    print("=" * 60)
    print(f"Test zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python versiyonu: {sys.version}")
    
    tests = [
        ("MediaPipe Kurulumu", test_1_mediapipe_kurulumu),
        ("Webcam Kontrolü", test_2_webcam_acma),
        ("Landmark Çıkarma", test_3_landmark_cikarma),
        ("Açı Hesaplama", test_4_aci_hesaplama),
        ("Veri Kaydetme", test_5_veri_kaydetme),
        ("Canlı Görüntü", test_6_canli_goruntu),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "✅ BAŞARILI" if result else "⚠️ SORUNLU"))
        except Exception as e:
            print(f"❌ Test sırasında hata: {e}")
            results.append((test_name, "❌ HATA"))
    
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI")
    print("=" * 60)
    for test_name, result in results:
        print(f"{test_name:.<30} {result}")
    
    success_count = sum(1 for _, r in results if "BAŞARILI" in r)
    print("=" * 60)
    print(f"✅ Başarılı: {success_count}/{len(tests)}")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()