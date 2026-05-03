import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure main is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient

# Mock ML components before importing main to prevent loading the real model
with patch('joblib.load') as mock_load:
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    # Assume mock expected features
    mock_load.return_value = {
        'model': mock_model,
        'scaler': mock_scaler,
        'features': ['CreditScore', 'Geography_Germany', 'Geography_Spain', 'Gender_Male', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary']
    }
    import main

client = TestClient(main.app)

class TestPredictChurnEndpoint(unittest.TestCase):
    def setUp(self):
        # We need to set the mock model and scaler directly in main since the top-level load happens once
        self.original_model = main.model
        self.original_scaler = main.scaler
        self.original_expected_features = main.expected_features

        main.model = MagicMock()
        main.scaler = MagicMock()
        main.expected_features = ['CreditScore', 'Geography_Germany', 'Geography_Spain', 'Gender_Male', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary']

        main.scaler.transform.return_value = [[0.5] * 11] # Dummy scaled input

        self.valid_payload = {
            "CreditScore": 600,
            "Geography": "France",
            "Gender": "Female",
            "Age": 40,
            "Tenure": 3,
            "Balance": 60000.0,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 50000.0
        }

    def tearDown(self):
        main.model = self.original_model
        main.scaler = self.original_scaler
        main.expected_features = self.original_expected_features

    def test_predict_churn_high_risk(self):
        main.model.predict_proba.return_value = [[0.15, 0.85]]
        main.model.predict.return_value = [1]

        response = client.post("/predict", json=self.valid_payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["churn_tahmini"], 1)
        self.assertEqual(data["churn_ihtimali"], 0.85)
        self.assertEqual(data["risk_seviyesi"], "Çok Yüksek Riskli - Acil İletişime Geçilmeli")
        self.assertEqual(data["mesaj"], "Tahmin başarıyla hesaplandı.")

    def test_predict_churn_medium_risk(self):
        main.model.predict_proba.return_value = [[0.4, 0.6]]
        main.model.predict.return_value = [1]

        response = client.post("/predict", json=self.valid_payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["churn_tahmini"], 1)
        self.assertEqual(data["churn_ihtimali"], 0.6)
        self.assertEqual(data["risk_seviyesi"], "Orta Riskli - Kampanya Önerilebilir")

    def test_predict_churn_low_risk(self):
        main.model.predict_proba.return_value = [[0.8, 0.2]]
        main.model.predict.return_value = [0]

        response = client.post("/predict", json=self.valid_payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["churn_tahmini"], 0)
        self.assertEqual(data["churn_ihtimali"], 0.2)
        self.assertEqual(data["risk_seviyesi"], "Düşük Riskli - Sadık Müşteri")

    def test_model_not_loaded_raises_500(self):
        main.model = None

        response = client.post("/predict", json=self.valid_payload)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Makine öğrenmesi modeli yüklenemedi.")

if __name__ == '__main__':
    unittest.main()
