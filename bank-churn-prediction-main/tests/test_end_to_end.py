import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock
import pytest

# Üst dizindeki modülleri içe aktarabilmek için sys.path güncelleniyor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
import main
from agents import run_agent

client = TestClient(app)

VALID_API_KEY = "test_super_secret_key"


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", VALID_API_KEY)
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
    "EstimatedSalary": 50000.0,
}


def test_end_to_end_churn_prediction_and_agent(mock_env, monkeypatch):
    """
    Uçtan uca test:
    1. FastAPI /predict endpoint'ine veri gönderilir.
    2. Model tahmini döner (mock).
    3. Dönen tahmin LangGraph ajanına beslenir.
    4. Ajanın doğru aksiyonu önerdiği doğrulanır.
    """

    prob = 0.85
    expected_risk = "Çok Yüksek Riskli - Acil İletişime Geçilmeli"

    # Modeli mockluyoruz
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[1 - prob, prob]]
    mock_model.predict.return_value = [1]

    # Scaler'ı mockluyoruz
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[0] * 11])

    monkeypatch.setattr(main, "model", mock_model)
    monkeypatch.setattr(main, "scaler", mock_scaler)
    monkeypatch.setattr(main, "expected_features", ["CreditScore", "Age"])

    headers = {"X-API-Key": VALID_API_KEY}

    # 1. API'ye İstek At
    response = client.post("/predict", headers=headers, json=sample_customer_data)

    # 2. Yanıtı Doğrula
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["risk_seviyesi"] == expected_risk
    assert json_data["churn_ihtimali"] == prob

    # 3. LangGraph ajanını çalıştır
    customer_id = "test_user_123"
    agent_result = run_agent(
        customer_id=customer_id,
        churn_probability=json_data["churn_ihtimali"],
        risk_level=json_data["risk_seviyesi"],
    )

    # 4. Ajan yanıtını doğrula
    assert agent_result["customer_id"] == customer_id
    assert agent_result["churn_probability"] == prob
    assert agent_result["risk_level"] == expected_risk
    assert (
        agent_result["recommended_action"] == "Acil İletişim & %20 İndirim Maili Gönder"
    )


def test_end_to_end_loyal_customer_agent(mock_env, monkeypatch):
    """
    Uçtan uca test: Düşük riskli müşteri
    """
    prob = 0.15
    expected_risk = "Düşük Riskli - Sadık Müşteri"

    # Modeli mockluyoruz
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[1 - prob, prob]]
    mock_model.predict.return_value = [0]

    # Scaler'ı mockluyoruz
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[0] * 11])

    monkeypatch.setattr(main, "model", mock_model)
    monkeypatch.setattr(main, "scaler", mock_scaler)
    monkeypatch.setattr(main, "expected_features", ["CreditScore", "Age"])

    headers = {"X-API-Key": VALID_API_KEY}

    # 1. API'ye İstek At
    response = client.post("/predict", headers=headers, json=sample_customer_data)

    # 2. Yanıtı Doğrula
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["risk_seviyesi"] == expected_risk
    assert json_data["churn_ihtimali"] == prob

    # 3. LangGraph ajanını çalıştır
    customer_id = "test_user_456"
    agent_result = run_agent(
        customer_id=customer_id,
        churn_probability=json_data["churn_ihtimali"],
        risk_level=json_data["risk_seviyesi"],
    )

    # 4. Ajan yanıtını doğrula
    assert agent_result["customer_id"] == customer_id
    assert agent_result["churn_probability"] == prob
    assert agent_result["risk_level"] == expected_risk
    assert agent_result["recommended_action"] == "İşlem Yok (Sadık Müşteri)"
