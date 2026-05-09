import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.model_metrics_service import (
    compute_all_metrics,
    create_confusion_matrix_fig,
    create_roc_curve_fig,
)

from unittest.mock import MagicMock

def test_compute_all_metrics():
    """Temel metriklerin hesaplanması test edilir."""
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([0, 1, 0, 0, 0])
    mock_model.predict_proba.return_value = np.array([[0.9, 0.1], [0.1, 0.9], [0.8, 0.2], [0.6, 0.4], [0.7, 0.3]])
    
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[0]*10]*5)
    
    df = pd.DataFrame({
        "CreditScore": [600, 700, 800, 500, 650],
        "Exited": [0, 1, 0, 1, 0]
    })
    features = ["CreditScore"]
    
    metrics = compute_all_metrics(mock_model, mock_scaler, features, df)
    assert metrics is not None
    assert "accuracy" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics
    assert metrics["accuracy"] > 0.0

def test_create_confusion_matrix_fig():
    """Karmaşıklık matrisi figürü oluşturulmalı."""
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0])
    fig = create_confusion_matrix_fig(y_true, y_pred)
    assert fig is not None

def test_create_roc_curve_fig():
    """ROC eğrisi figürü oluşturulmalı."""
    y_true = np.array([0, 1, 0, 1])
    y_prob = np.array([0.2, 0.8, 0.3, 0.7])
    fig = create_roc_curve_fig(y_true, y_prob)
    assert fig is not None
