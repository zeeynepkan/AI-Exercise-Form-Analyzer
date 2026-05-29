# Bitirme Sunumu - Konuşma Metni (Türkçe)

Merhaba, ben [Ad Soyad].  
Bugün bitirme projem olan **Akıllı Egzersiz Form Analizi** uygulamasını sunacağım.

## 1. Problem
Evde spor yapan kullanıcılar çoğunlukla bir eğitmen desteği olmadan egzersiz yapıyor.  
Bu da hareketlerin yanlış formda tekrar edilmesine ve sakatlık riskinin artmasına neden olabiliyor.

Bu projede amacım, mobil cihaz kamerasını kullanarak kullanıcıya anlık geri bildirim veren, pratik bir form analiz sistemi geliştirmekti.

## 2. Çözüm
Geliştirdiğim uygulama, kameradan aldığı görüntüde insan iskelet noktalarını çıkarıyor, açı ve oran gibi özellikler üretiyor, ardından bir yapay zeka modeliyle formun doğru mu yanlış mı olduğunu tahmin ediyor.

Desteklenen egzersizler:
- Squat
- Lunge
- Diz üstü şınav
- Bridge

## 3. Teknik Mimari
Sistem şu adımlardan oluşuyor:
1. MediaPipe Pose ile landmark tespiti
2. Özellik çıkarımı (eklem açıları, mesafe ve oranlar)
3. Normalizasyon (eğitimde kullanılan scaler parametreleriyle)
4. MLP model ile tahmin
5. Kural tabanlı kalite puanı ile hibrit değerlendirme

Yani sadece model çıktısına bağlı kalmadım; hareket fiziğine dayalı kurallarla modeli destekledim.

## 4. Önemli İyileştirmeler
Projenin ilerleyen aşamasında birkaç kritik iyileştirme yaptım:

- **Aktif faz kontrolü:** Kullanıcı ayakta beklerken model değerlendirme yapmıyor.
- **Hibrit skor:**  
  Final skor = `0.7 * model + 0.3 * kural skoru`  
  Bu sayede yanlış forma rağmen “correct” verme oranı düştü.
- **Egzersize özel ipuçları:** Her hareket için farklı düzeltme önerileri
- **Sesli geri bildirim:** Türkçe ve İngilizce destek
- **Dil ve tema kalıcılığı:** Kullanıcı tercihi uygulama yeniden açıldığında korunuyor
- **Oturum özeti:** Süre, tekrar sayısı, doğru form yüzdesi

## 5. Kullanıcı Arayüzü
Ana ekranda egzersiz seçim kartları bulunuyor.  
Egzersiz ekranında:
- Canlı iskelet çizimi
- Hedef açı aralığı
- Skor ve geri bildirim
- Sesli yönlendirme

Egzersiz bitince kullanıcıya özet ekranı gösteriliyor.

## 6. Katkı ve Sonuç
Bu proje ile:
- Gerçek zamanlı çalışan bir mobil form analiz sistemi geliştirdim.
- Cihaz üstünde çalışan, gizlilik odaklı bir çözüm sundum.
- Model tabanlı yaklaşımı kural tabanlı doğrulama ile birleştirerek daha güvenilir bir geri bildirim mekanizması oluşturdum.

## 7. Gelecek Çalışmalar
İleride:
- Kişiye özel eşik optimizasyonu,
- Daha fazla egzersiz türü,
- Sekans tabanlı daha güçlü modeller,
- Uzun dönem ilerleme takibi
eklenebilir.

Dinlediğiniz için teşekkür ederim.  
Sorularınızı memnuniyetle cevaplayabilirim.
