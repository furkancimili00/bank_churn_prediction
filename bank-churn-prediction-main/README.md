# 🏦 Banka Müşteri Churn Tahmin ve Karar Destek Platformu

[![CI Pipeline](https://github.com/furkancimili00/bank_churn_prediction/actions/workflows/ci.yml/badge.svg)](https://github.com/furkancimili00/bank_churn_prediction/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Akademik tez çalışmasından kurumsal düzeyde bir Karar Destek Platformu'na dönüştürülmüş, XAI destekli müşteri churn tahmin sistemi.**

---

## 🎯 Akademik Hedef Metrikler

| Metrik | Hedef | Durum |
|:---|:---|:---|
| F1 Score | > 0.85 | ✅ |
| ROC-AUC | > 0.90 | ✅ |
| API Yanıt Süresi | < 1 saniye | ✅ |
| Disparate Impact | < 1.2 | ✅ |

---

## ⚙️ Teknoloji Yığını

| Katman | Teknoloji |
|:---|:---|
| **ML Model** | XGBoost + SMOTE + GridSearchCV |
| **Açıklanabilirlik** | SHAP (TreeExplainer) |
| **Backend API** | FastAPI + slowapi (Rate Limiting) + CORS |
| **Frontend** | Streamlit (12 sekmeli dashboard) |
| **Ajan Sistemi** | LangGraph (4 düğümlü çok adımlı akış) |
| **LLM Entegrasyonu** | Gemini / OpenAI (Opsiyonel, kural tabanlı fallback) |
| **Loglama** | Loguru (JSON formatı, dosya rotasyonu) |
| **Containerization** | Docker (multi-stage build) + docker-compose |
| **CI/CD** | GitHub Actions (lint → test → build) |
| **Güvenlik** | API Key auth, KVKK/GDPR maskeleme, audit log |

---

## 📊 Dashboard Sekmeleri (12 Modül)

| # | Sekme | Açıklama |
|:---|:---|:---|
| 1 | 👤 Tekil Analiz | Müşteri parametrelerini girerek churn tahmini + SHAP açıklaması |
| 2 | 🧪 What-If | Parametreleri değiştirerek risk değişimini simüle etme |
| 3 | 📂 Toplu Analiz | CSV yükleme ile toplu müşteri risk değerlendirmesi |
| 4 | 📝 Yönetim Raporu | LLM destekli (fallback: kural tabanlı) yönetim özeti |
| 5 | 📈 EDA | Korelasyon, dağılım, box-plot, sunburst analizi |
| 6 | 🏆 Performans | Confusion matrix, ROC/PR eğrileri, tez hedef karşılaştırması |
| 7 | 🎯 Segmentasyon | K-Means kümeleme, PCA scatter, radar profil |
| 8 | ⚖️ Adillik | Disparate impact, cinsiyet/coğrafya bias analizi |
| 9 | 👤 Profil Kartı | 360° müşteri görünümü, SHAP waterfall, benzer müşteriler |
| 10 | 🔒 Gizlilik | KVKK/GDPR uyumlu veri anonimleştirme (hash/partial/redact) |
| 11 | 📉 Drift Analizi | PSI ve KS testi ile veri dağılım kayması tespiti |
| 12 | 📜 Denetim Günlüğü | Tüm işlemlerin zaman damgalı audit kaydı |

---

## 🚀 Kurulum ve Çalıştırma

### Yerel Ortam

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Sistemi başlat (API + Dashboard)
python run.py
```

- **API Swagger:** http://127.0.0.1:8000/docs
- **Dashboard:** http://127.0.0.1:8501
- **Giriş:** Kullanıcı: `admin`, Şifre: `123456`

### Docker

```bash
docker-compose up --build
```

---

## 🔌 API Endpoint'leri

| Method | Endpoint | Açıklama |
|:---|:---|:---|
| `GET` | `/` | Sağlık kontrolü |
| `GET` | `/model-info` | Model metadata (versiyon, özellikler) |
| `POST` | `/predict` | Tekil müşteri tahmini |
| `POST` | `/batch-predict` | Toplu tahmin (max 1000 müşteri) |
| `GET` | `/audit/logs` | Denetim günlüğü kayıtları |

> Tüm endpoint'ler `X-API-Key` başlığı gerektirir.

---

## 🧪 Testler

```bash
# Tüm testleri çalıştır
python -m pytest tests/ -v

# QA Agent kontrolü
python qa_agent.py
```

---

## 📁 Proje Yapısı

```
├── main.py                    # FastAPI backend (API endpoint'leri)
├── dashboard.py               # Streamlit frontend (12 sekmeli panel)
├── run.py                     # Tek komutla tüm sistemi başlatma
├── core/                      # Temel altyapı bileşenleri
│   ├── logging_config.py      # Loguru yapılandırması
│   └── utils.py               # Veri ön işleme yardımcıları
├── services/                  # İş mantığı servisleri
│   ├── prediction.py          # Tahmin işlemleri ve SHAP
│   ├── eda_service.py         # Keşifsel veri analizi
│   ├── model_metrics_service.py # Model performans metrikleri
│   ├── segmentation_service.py# K-Means segmentasyonu
│   ├── fairness_service.py    # Adillik/bias analizi
│   ├── customer_profile_service.py # 360° müşteri profil kartı
│   ├── data_privacy.py        # KVKK/GDPR veri maskeleme
│   ├── drift_service.py       # Veri drift tespiti
│   └── audit_service.py       # Denetim günlüğü
├── agents/                    # LangGraph ajan sistemi
│   ├── churn_agent.py         # Çok adımlı analiz akışı
│   └── qa_agent.py            # Otomatik QA doğrulama ajanı
├── scripts/                   # Model eğitimi ve betikler
│   ├── train_model.py         # Model eğitim pipeline'ı
│   └── create_synthetic_dataset.py # Sentetik veri üretimi
├── tests/                     # Birim ve entegrasyon testleri
├── Dockerfile                 # Multi-stage Docker yapılandırması
├── docker-compose.yml         # API + Frontend orkestrasyon
├── .github/workflows/ci.yml   # CI/CD pipeline
└── .streamlit/secrets.toml    # Kimlik doğrulama ve LLM API anahtarları
```

---

## 🌍 SDG Uyumluluk

- **SDG 8:** İnsana Yakışır İş ve Ekonomik Büyüme
- **SDG 10:** Eşitsizliklerin Azaltılması (Fairness/Bias analizi)

---

*v2.0.0 — Kurumsal Karar Destek Platformu*