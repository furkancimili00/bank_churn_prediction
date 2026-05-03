from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_predict_churn_model_missing():
    """
    Model yüklenemediğinde (None olduğunda) /predict endpoint'inin
    500 hata kodu döndürdüğünü doğrular.
    """
    # 'main.model' değişkenini None olarak mock'lıyoruz.
    # Bu, 'main.py' içindeki 'if model is None' kontrolünü tetikleyecektir.
    with patch('main.model', None):
        # API'ye gönderilecek örnek müşteri verisi
        payload = {
            "CreditScore": 600,
            "Geography": "France",
            "Gender": "Male",
            "Age": 42,
            "Tenure": 5,
            "Balance": 50000.0,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 40000.0
        }

        # POST isteği gönderiyoruz
        response = client.post("/predict", json=payload)

        # Yanıtın 500 Internal Server Error olduğunu doğruluyoruz
        assert response.status_code == 500

        # Hata mesajının doğruluğunu kontrol ediyoruz
        assert response.json()["detail"] == "Makine öğrenmesi modeli yüklenemedi."
