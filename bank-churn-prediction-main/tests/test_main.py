import sys
import os

# Üst dizindeki modülleri içe aktarabilmek için sys.path güncelleniyor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)

def test_health_check() -> None:
    """
    Health check (/) endpoint'inin doğru çalışıp çalışmadığını test eder.

    Beklenen Davranış:
        - 200 OK HTTP durum kodu döndürmelidir.
        - JSON yanıtında status 'success' ve API'nin aktif olduğunu belirten bir mesaj yer almalıdır.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Churn Tahmin API aktif olarak çalışıyor."}

def test_api_key_missing_server_side(monkeypatch):
    """Test when CHURN_API_KEY is missing on the server side."""
    monkeypatch.setattr(main, "API_KEY", None)
    response = client.post("/predict", headers={"X-API-Key": "any-key"}, json={})
    assert response.status_code == 500
    assert response.json() == {"detail": "API anahtarı sunucu tarafında yapılandırılmamış."}

def test_api_key_invalid(monkeypatch):
    """Test with an invalid API key."""
    monkeypatch.setattr(main, "API_KEY", "test-secret-key")
    response = client.post("/predict", headers={"X-API-Key": "wrong-key"}, json={})
    assert response.status_code == 401
    assert response.json() == {"detail": "Geçersiz veya eksik API Anahtarı"}

def test_api_key_missing_client_side(monkeypatch):
    """Test when the client does not provide an API key."""
    monkeypatch.setattr(main, "API_KEY", "test-secret-key")
    # The Depends(api_key_header_scheme) will auto_error=False, so get_api_key gets None
    response = client.post("/predict", json={})
    assert response.status_code == 401
    assert response.json() == {"detail": "Geçersiz veya eksik API Anahtarı"}

def test_predict_model_not_loaded(monkeypatch):
    """Test when the ML model fails to load."""
    monkeypatch.setattr(main, "API_KEY", "test-secret-key")
    monkeypatch.setattr(main, "model", None)

    response = client.post("/predict", headers={"X-API-Key": "test-secret-key"}, json={
        "CreditScore": 600, "Geography": "France", "Gender": "Male",
        "Age": 40, "Tenure": 3, "Balance": 60000.0,
        "NumOfProducts": 2, "HasCrCard": 1, "IsActiveMember": 1,
        "EstimatedSalary": 50000.0
    })

    assert response.status_code == 500
    assert response.json() == {"detail": "Makine öğrenmesi modeli yüklenemedi."}

def test_predict_success_high_risk(monkeypatch):
    """Test a successful prediction returning high risk."""
    monkeypatch.setattr(main, "API_KEY", "test-secret-key")

    mock_model = MagicMock()
    mock_model.predict.return_value = [1]
    mock_model.predict_proba.return_value = [[0.2, 0.85]]
    monkeypatch.setattr(main, "model", mock_model)

    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = [[0.5] * 10]
    monkeypatch.setattr(main, "scaler", mock_scaler)

    monkeypatch.setattr(main, "expected_features", ["CreditScore", "Age"])

    response = client.post("/predict", headers={"X-API-Key": "test-secret-key"}, json={
        "CreditScore": 600, "Geography": "France", "Gender": "Male",
        "Age": 40, "Tenure": 3, "Balance": 60000.0,
        "NumOfProducts": 2, "HasCrCard": 1, "IsActiveMember": 1,
        "EstimatedSalary": 50000.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["churn_tahmini"] == 1
    assert data["churn_ihtimali"] == 0.85
    assert data["risk_seviyesi"] == "Çok Yüksek Riskli - Acil İletişime Geçilmeli"

def test_predict_success_medium_risk(monkeypatch):
    """Test a successful prediction returning medium risk."""
    monkeypatch.setattr(main, "API_KEY", "test-secret-key")

    mock_model = MagicMock()
    mock_model.predict.return_value = [1]
    mock_model.predict_proba.return_value = [[0.4, 0.55]]
    monkeypatch.setattr(main, "model", mock_model)

    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = [[0.5] * 10]
    monkeypatch.setattr(main, "scaler", mock_scaler)

    monkeypatch.setattr(main, "expected_features", ["CreditScore", "Age"])

    response = client.post("/predict", headers={"X-API-Key": "test-secret-key"}, json={
        "CreditScore": 600, "Geography": "France", "Gender": "Male",
        "Age": 40, "Tenure": 3, "Balance": 60000.0,
        "NumOfProducts": 2, "HasCrCard": 1, "IsActiveMember": 1,
        "EstimatedSalary": 50000.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["risk_seviyesi"] == "Orta Riskli - Kampanya Önerilebilir"

def test_predict_success_low_risk(monkeypatch):
    """Test a successful prediction returning low risk."""
    monkeypatch.setattr(main, "API_KEY", "test-secret-key")

    mock_model = MagicMock()
    mock_model.predict.return_value = [0]
    mock_model.predict_proba.return_value = [[0.8, 0.20]]
    monkeypatch.setattr(main, "model", mock_model)

    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = [[0.5] * 10]
    monkeypatch.setattr(main, "scaler", mock_scaler)

    monkeypatch.setattr(main, "expected_features", ["CreditScore", "Age"])

    response = client.post("/predict", headers={"X-API-Key": "test-secret-key"}, json={
        "CreditScore": 600, "Geography": "France", "Gender": "Male",
        "Age": 40, "Tenure": 3, "Balance": 60000.0,
        "NumOfProducts": 2, "HasCrCard": 1, "IsActiveMember": 1,
        "EstimatedSalary": 50000.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["risk_seviyesi"] == "Düşük Riskli - Sadık Müşteri"
