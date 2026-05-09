import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.eda_service import (
    load_default_dataset,
    create_correlation_heatmap,
    create_distribution_histograms,
    get_summary_statistics,
)

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "CreditScore": [600, 700, 800],
        "Age": [30, 40, 50],
        "Tenure": [2, 5, 8],
        "Balance": [50000, 60000, 70000],
        "NumOfProducts": [1, 2, 1],
        "EstimatedSalary": [40000, 50000, 60000],
        "Exited": [0, 1, 0]
    })

def test_load_default_dataset_not_found():
    """Dosya bulunamadığında None dönmeli."""
    df = load_default_dataset("olmayan_dosya.csv")
    assert df is None

def test_create_correlation_heatmap(sample_df):
    """Korelasyon matrisi figürü oluşturulmalı."""
    fig = create_correlation_heatmap(sample_df)
    assert fig is not None
    assert "data" in fig

def test_create_distribution_histograms(sample_df):
    """Dağılım grafiği oluşturulmalı."""
    fig = create_distribution_histograms(sample_df)
    assert fig is not None

def test_get_summary_statistics(sample_df):
    """Özet istatistikler doğru hesaplanmalı."""
    stats = get_summary_statistics(sample_df)
    assert stats["toplam_musteri"] == 3
    assert stats["ortalama_yas"] == 40.0
    assert stats["churn_sayisi"] == 1
