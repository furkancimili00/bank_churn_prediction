# Mimari Dokümantasyon

## Sistem Tasarımı
Sistem iki ana modülden oluşur:
1. **FastAPI (Backend):** Rate limiting ve model servisinden sorumlu mikroservis. Core ve Services modüllerini içerir.
2. **Streamlit (Frontend):** Yönetici paneli ve görselleştirme için kullanılan arayüz. UI modülü altında klasörlenmiştir.

## Veri Akışı
1. Müşteri verisi sisteme JSON üzerinden girer.
2. `core/utils.py` içindeki `preprocess_data` on-hot encoding ve scaling işlemlerini yapar.
3. `XGBClassifier` ile `.skops` dosyasından yüklenen model tahmin yapar.
4. Model metrikleri dashboard/API üzerinden son kullanıcıya sunulur.
