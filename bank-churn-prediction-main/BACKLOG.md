# 📋 Banka Churn Tahmini Projesi - İş Emri (Backlog)

Bu dosya sistemin otonom AI ajanları ve geliştirici ekibi için bir yol haritası niteliğindedir. Görevler öncelik sırasına göre listelenmiştir.

## 🔴 P1: Kritik Öncelikli Görevler (Yüksek Etki / Acil)
- [ ] **LangGraph Tabanlı Ajan Mimarisinin Kurulması (`agents.py`):**
  - Otonom ajanların banka personeline veya müşteriye otomatik aksiyonlar (örn. indirim maili) önerebileceği/kendi kendine çalışabileceği bir akış tasarlanmalı.
- [ ] **FastAPI Güvenlik Güncellemesi:**
  - `main.py` içerisindeki `predict` endpoint'inde aşırı yüklemelere (DoS) karşı rate limiting altyapısı (örn: `slowapi`) kurulmalı.
- [ ] **Streamlit Dosya Yükleme Güvenliği:**
  - `dashboard.py` üzerindeki toplu tahmin yükleme ekranında CSV dosyaları için katı doğrulama (şema, boyut ve satır limiti) kuralları uygulanmalı.

## 🟡 P2: Orta Öncelikli Görevler (Gelişmiş Analitik ve Optimizasyon)
- [ ] **Gelişmiş CLTV (Customer Lifetime Value) İndikatörü:**
  - Churn olması muhtemel müşteriler için sadece riski değil, bankaya net maliyeti tahmin eden, harcama alışkanlıklarını dahil eden daha karmaşık bir CLTV modeli entegre edilmeli.
- [ ] **Hiperparametre Optimizasyonu (Optuna):**
  - GridSearch yerine Optuna kütüphanesi kullanılarak daha verimli, bayesian-bazlı bir model optimizasyonu geliştirilmeli.
- [ ] **SHAP ve Açıklanabilirlik Performansı (Caching):**
  - Streamlit dashboard'daki SHAP TreeExplainer hesaplamalarının performansı için `st.cache_resource` doğru ve asenkron uyarı bırakmayacak şekilde entegre edilmeli.

## 🟢 P3: Düşük Öncelikli Görevler (Teknik Borç ve İzleme)
- [ ] **Loglama Altyapısı (Logging):**
  - `print` yerine Python'ın standart `logging` veya modern `loguru` paketine geçilmeli.
- [ ] **Test Coverage Artırımı:**
  - `tests/test_dashboard.py` için Streamlit AppTest senaryoları artırılmalı ve kapsam (coverage) %90'ın üzerine çekilmeli.
- [ ] **Prometheus ve Grafana Entegrasyonu:**
  - FastAPI metriklerinin ve model tahmin dağılımlarının canlı olarak izlenebileceği bir dashboard oluşturulmalı.
