import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import app, CustomerData
import main

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Churn Tahmin API aktif olarak çalışıyor."}

def test_predict_model_not_loaded(monkeypatch):
    monkeypatch.setattr(main, "model", None)
    customer_data = {
        "CreditScore": 600,
        "Geography": "France",
        "Gender": "Male",
        "Age": 40,
        "Tenure": 3,
        "Balance": 60000.0,
        "NumOfProducts": 2,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 50000.0
    }
    response = client.post("/predict", json=customer_data)
    assert response.status_code == 500
    assert response.json() == {"detail": "Makine öğrenmesi modeli yüklenemedi."}


@pytest.mark.parametrize("prob, risk_level_msg", [
    (0.75, "Çok Yüksek Riskli - Acil İletişime Geçilmeli"),
    (0.45, "Orta Riskli - Kampanya Önerilebilir"),
    (0.15, "Düşük Riskli - Sadık Müşteri"),
])
def test_predict_churn_success(prob, risk_level_msg, monkeypatch):
    # Mocking model methods
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[1 - prob, prob]]
    mock_model.predict.return_value = [1 if prob >= 0.5 else 0]

    # Mocking scaler method
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = [[1.0] * 12]  # Dummy data

    # Setting the mocks to main module
    monkeypatch.setattr(main, "model", mock_model)
    monkeypatch.setattr(main, "scaler", mock_scaler)
    monkeypatch.setattr(main, "expected_features", ["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember", "EstimatedSalary", "Geography_Germany", "Geography_Spain", "Gender_Male"])

    customer_data = {
        "CreditScore": 600,
        "Geography": "France",
        "Gender": "Male",
        "Age": 40,
        "Tenure": 3,
        "Balance": 60000.0,
        "NumOfProducts": 2,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 50000.0
    }

    response = client.post("/predict", json=customer_data)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["churn_tahmini"] == (1 if prob >= 0.5 else 0)
    assert json_data["churn_ihtimali"] == prob
    assert json_data["risk_seviyesi"] == risk_level_msg
    assert json_data["mesaj"] == "Tahmin başarıyla hesaplandı."
