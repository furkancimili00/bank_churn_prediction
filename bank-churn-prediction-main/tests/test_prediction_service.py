import os
import sys
from unittest.mock import MagicMock

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.prediction_service import PredictionService


def _create_service(probabilities: np.ndarray, predictions: np.ndarray) -> PredictionService:
    """Sahte model ve scaler ile tahmin servisi olusturur."""
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = probabilities
    mock_model.predict.return_value = predictions

    mock_scaler = MagicMock()
    mock_scaler.transform.side_effect = lambda frame: frame.to_numpy()

    return PredictionService(
        model=mock_model,
        scaler=mock_scaler,
        expected_features=["CreditScore", "Age"],
    )


def test_prediction_service_predict_one_returns_risk_result() -> None:
    """Tekil tahmin sonucu olasilik, sinif ve risk seviyesini dondurmeli."""
    service = _create_service(
        probabilities=np.array([[0.15, 0.85]]),
        predictions=np.array([1]),
    )

    result = service.predict_one({"CreditScore": 650, "Age": 42})

    assert result["churn_tahmini"] == 1
    assert result["churn_ihtimali"] == 0.85
    assert result["risk_seviyesi"] == "Çok Yüksek Riskli - Acil İletişime Geçilmeli"


def test_prediction_service_predict_batch_returns_summary() -> None:
    """Toplu tahmin ozeti risk seviyelerine gore dogru hesaplanmali."""
    service = _create_service(
        probabilities=np.array([[0.10, 0.90], [0.55, 0.45], [0.85, 0.15]]),
        predictions=np.array([1, 1, 0]),
    )

    result = service.predict_batch(
        [
            {"CreditScore": 700, "Age": 30},
            {"CreditScore": 620, "Age": 44},
            {"CreditScore": 580, "Age": 52},
        ]
    )

    assert result["toplam_musteri"] == 3
    assert result["ozet"]["yuksek_riskli"] == 1
    assert result["ozet"]["orta_riskli"] == 1
    assert result["ozet"]["dusuk_riskli"] == 1
    assert len(result["sonuclar"]) == 3


def test_prediction_service_predict_probabilities_uses_preprocessing() -> None:
    """Toplu olasilik tahmini preprocessing adimini kullanmali."""
    service = _create_service(
        probabilities=np.array([[0.75, 0.25]]),
        predictions=np.array([0]),
    )
    customers = pd.DataFrame([{"CreditScore": 720, "Age": 35}])

    probabilities = service.predict_probabilities(customers)

    assert probabilities.tolist() == [0.25]
    service.scaler.transform.assert_called_once()


def test_prediction_service_is_ready_requires_artifacts() -> None:
    """Model bilesenlerinden biri eksikse servis hazir kabul edilmemeli."""
    service = PredictionService(model=None, scaler=MagicMock(), expected_features=["Age"])

    assert service.is_ready() is False
