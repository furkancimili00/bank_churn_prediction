import sys
import os
from unittest.mock import patch, MagicMock
import pytest

# Üst dizindeki modülleri içe aktarabilmek için sys.path güncelleniyor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app
import main

client = TestClient(app)

# Orijinal modülü değiştirmeden önce geçerli bir API anahtarı belirliyoruz
# Bunu main modülüne monkeypatch ile uygulayacağız
VALID_API_KEY = "test_super_secret_key"

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

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setattr(main, 'API_KEY', VALID_API_KEY)
    yield

# Örnek müşteri verisi
sample_customer_data = {
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

def test_predict_unauthorized_missing_key(mock_env):
    """API anahtarı gönderilmediğinde 401 Unauthorized dönmeli"""
    response = client.post("/predict", json=sample_customer_data)
    assert response.status_code == 401
    assert "Geçersiz veya eksik API Anahtarı" in response.json()["detail"] or "Not authenticated" in response.json()["detail"]

def test_predict_unauthorized_invalid_key(mock_env):
    """Yanlış API anahtarı gönderildiğinde 401 Unauthorized dönmeli"""
    headers = {"X-API-Key": "wrong_key"}
    response = client.post("/predict", headers=headers, json=sample_customer_data)
    assert response.status_code == 401
    assert "Geçersiz veya eksik API Anahtarı" in response.json()["detail"]

def test_predict_server_error_no_api_key_configured(monkeypatch):
    """Sunucuda API anahtarı yapılandırılmamışsa 500 Internal Server Error dönmeli"""
    monkeypatch.setattr(main, 'API_KEY', None)
    headers = {"X-API-Key": "some_key"}
    response = client.post("/predict", headers=headers, json=sample_customer_data)
    assert response.status_code == 500
    assert "API anahtarı sunucu tarafında yapılandırılmamış" in response.json()["detail"]

def test_predict_model_not_loaded(mock_env, monkeypatch):
    """Model yüklenememişse (None ise) 500 dönmeli"""
    monkeypatch.setattr(main, 'model', None)
    headers = {"X-API-Key": VALID_API_KEY}
    response = client.post("/predict", headers=headers, json=sample_customer_data)
    assert response.status_code == 500
    assert "Makine öğrenmesi modeli yüklenemedi" in response.json()["detail"]

@pytest.mark.parametrize("prob, expected_risk", [
    (0.80, "Çok Yüksek Riskli - Acil İletişime Geçilmeli"),
    (0.50, "Orta Riskli - Kampanya Önerilebilir"),
    (0.20, "Düşük Riskli - Sadık Müşteri")
])
def test_predict_success_different_risk_levels(prob, expected_risk, mock_env, monkeypatch):
    """Geçerli veri ile model tahmini yapıldığında risk seviyeleri doğru dönmeli"""
    # Modeli mockluyoruz
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[1 - prob, prob]]
    mock_model.predict.return_value = [1 if prob >= 0.5 else 0]

    # Scaler'ı mockluyoruz
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = [[0] * 10] # Dummy dönüştürülmüş veri

    monkeypatch.setattr(main, 'model', mock_model)
    monkeypatch.setattr(main, 'scaler', mock_scaler)
    monkeypatch.setattr(main, 'expected_features', ['CreditScore', 'Age']) # Dummy features

    headers = {"X-API-Key": VALID_API_KEY}
    response = client.post("/predict", headers=headers, json=sample_customer_data)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["risk_seviyesi"] == expected_risk
    assert json_data["churn_ihtimali"] == prob
    assert "churn_tahmini" in json_data

def test_predict_rate_limit(mock_env, monkeypatch):
    """
    /predict endpoint'ine art arda çok sayıda (10'dan fazla) istek atıldığında
    rate limiting mekanizmasının devreye girip 429 döndürdüğünü test eder.
    """
    # Modeli ve scaler'ı mockluyoruz ki testler hızlı çalışsın
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.8, 0.2]]
    mock_model.predict.return_value = [0]

    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = [[0] * 10]

    monkeypatch.setattr(main, 'model', mock_model)
    monkeypatch.setattr(main, 'scaler', mock_scaler)
    monkeypatch.setattr(main, 'expected_features', ['CreditScore'])

    headers = {"X-API-Key": VALID_API_KEY}

    # Yeni bir client kullanalım (Rate limit remote_address'e baktığı için TestClient'te bazen IP sorunu olabilir ama varsayılan olarak testserver kullanır)
    client_rl = TestClient(app)

    # Önceki testlerden kalan limitleri sıfırlamak için limiter'ı temizliyoruz
    app.state.limiter.reset()

    # Rate limit 10/minute, o yüzden 10 tane başarılı istek atıyoruz
    for _ in range(10):
        response = client_rl.post("/predict", headers=headers, json=sample_customer_data)
        assert response.status_code == 200

    # 11. isteğin 429 Too Many Requests dönmesi gerekir
    response = client_rl.post("/predict", headers=headers, json=sample_customer_data)
    assert response.status_code == 429
