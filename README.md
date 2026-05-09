# Banka Churn Risk Tahmin Platformu

## Proje Özeti
Bu proje, müşteri terk (churn) riskini XAI (Explainable AI) destekli olarak hesaplayan kurumsal bir makine öğrenmesi API & Dashboard çözümüdür. FastAPI üzerinden servis edilen XGBoost modeli, Streamlit arayüzü ile son kullanıcılara sunulur.

## Teknoloji Yığını
- **Model:** XGBoost + SHAP (Explainability)
- **Backend:** FastAPI, Uvicorn, SlowAPI
- **Frontend:** Streamlit, Plotly
- **Deploy:** Docker (Multi-stage build)

## Tez/Hedef Metrikleri
- ✅ F1 Score > 0.85
- ✅ ROC-AUC > 0.90
- ✅ API Yanıt < 1s

## Kurulum ve Çalıştırma
pip install -r requirements.txt
docker-compose up --build

