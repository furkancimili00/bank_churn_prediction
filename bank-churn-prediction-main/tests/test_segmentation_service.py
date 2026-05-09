import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.segmentation_service import (
    find_optimal_k,
    perform_segmentation,
    create_segment_summary_table,
)

@pytest.fixture
def sample_df():
    # K-Means için yeterli çeşitlilikte veri
    return pd.DataFrame({
        "CreditScore": np.random.randint(400, 800, 50),
        "Age": np.random.randint(18, 80, 50),
        "Tenure": np.random.randint(0, 10, 50),
        "Balance": np.random.uniform(0, 100000, 50),
        "NumOfProducts": np.random.randint(1, 4, 50),
        "EstimatedSalary": np.random.uniform(20000, 150000, 50),
        "Exited": np.random.randint(0, 2, 50)
    })

def test_find_optimal_k(sample_df):
    """Elbow metodu figürü oluşturulmalı."""
    fig = find_optimal_k(sample_df, max_k=4)
    assert fig is not None

def test_perform_segmentation(sample_df):
    """Segmentasyon başarıyla uygulanmalı ve Segment sütunu eklenmeli."""
    df_res, X_scaled, scaler = perform_segmentation(sample_df, n_clusters=3)
    assert "Segment" in df_res.columns
    assert "Segment_Adi" in df_res.columns
    assert len(df_res["Segment"].unique()) == 3

def test_create_segment_summary_table(sample_df):
    """Özet tablosu hata vermeden oluşturulmalı."""
    df_res, _, _ = perform_segmentation(sample_df, n_clusters=2)
    fig = create_segment_summary_table(df_res)
    assert fig is not None
