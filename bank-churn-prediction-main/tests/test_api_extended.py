import sys
import os
import pytest

# Proje ana dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock
import numpy as np
from fastapi.testclient import TestClient

# Test ortamı için API key ayarla
os.environ["CHURN_API_KEY"] = "test_api_key_123"

from main import app

client = TestClient(app)
VALID_API_KEY = "test_api_key_123"

# Test verisi
sample_customer = {
    "CreditScore": 600,
    "Geography": "France",
    "Gender": "Male",
    "Age": 40,
    "Tenure": 3,
    "Balance": 60000.0,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 50000.0,
}


class TestModelInfoEndpoint:
    """Model bilgi endpoint'i testleri."""

    def test_model_info_success(self):
        """Model-info endpoint'i doğru metadata döner."""
        headers = {"X-API-Key": VALID_API_KEY}
        response = client.get("/model-info", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "api_version" in data
        assert "model_type" in data
        assert "features" in data
        assert "risk_thresholds" in data
        assert data["status"] == "aktif"

    def test_model_info_unauthorized(self):
        """API anahtarı olmadan erişim reddedilir."""
        response = client.get("/model-info")
        assert response.status_code == 401


class TestBatchPredictEndpoint:
    """Toplu tahmin endpoint'i testleri."""

    def test_batch_predict_success(self, monkeypatch):
        """İki müşteri için toplu tahmin başarıyla döner."""
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = np.array([[0.3, 0.7], [0.8, 0.2]])
        mock_model.predict.return_value = np.array([1, 0])

        mock_scaler = MagicMock()
        mock_scaler.transform.return_value = np.array([[0] * 11, [0] * 11])

        import main
        monkeypatch.setattr(main, "model", mock_model)
        monkeypatch.setattr(main, "scaler", mock_scaler)
        monkeypatch.setattr(main, "expected_features", ["CreditScore", "Age"])

        headers = {"X-API-Key": VALID_API_KEY}
        payload = {"customers": [sample_customer, sample_customer]}

        response = client.post("/batch-predict", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["toplam_musteri"] == 2
        assert "ozet" in data
        assert "sonuclar" in data
        assert len(data["sonuclar"]) == 2

    def test_batch_predict_empty_list(self):
        """Boş müşteri listesi 400 hatası döner."""
        headers = {"X-API-Key": VALID_API_KEY}
        payload = {"customers": []}

        response = client.post("/batch-predict", headers=headers, json=payload)
        assert response.status_code == 400

    def test_batch_predict_unauthorized(self):
        """API anahtarı olmadan erişim reddedilir."""
        payload = {"customers": [sample_customer]}
        response = client.post("/batch-predict", json=payload)
        assert response.status_code == 401

    def test_batch_predict_summary_stats(self, monkeypatch):
        """Toplu tahmin özet istatistikleri doğru hesaplanır."""
        mock_model = MagicMock()
        # 1 yüksek, 1 orta, 1 düşük riskli
        mock_model.predict_proba.return_value = np.array([[0.1, 0.9], [0.55, 0.45], [0.85, 0.15]])
        mock_model.predict.return_value = np.array([1, 1, 0])

        mock_scaler = MagicMock()
        mock_scaler.transform.return_value = np.array([[0] * 11] * 3)

        import main
        monkeypatch.setattr(main, "model", mock_model)
        monkeypatch.setattr(main, "scaler", mock_scaler)
        monkeypatch.setattr(main, "expected_features", ["CreditScore", "Age"])

        headers = {"X-API-Key": VALID_API_KEY}
        payload = {"customers": [sample_customer, sample_customer, sample_customer]}

        response = client.post("/batch-predict", headers=headers, json=payload)
        data = response.json()

        assert data["ozet"]["yuksek_riskli"] == 1
        assert data["ozet"]["orta_riskli"] == 1
        assert data["ozet"]["dusuk_riskli"] == 1
