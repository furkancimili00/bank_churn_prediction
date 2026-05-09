import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.utils import preprocess_data
from sklearn.preprocessing import StandardScaler

@pytest.fixture
def dummy_scaler():
    scaler = StandardScaler()
    scaler.fit(np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]))
    return scaler

def test_preprocess_handles_missing_columns(dummy_scaler):
    data = {"CreditScore": [600]}
    df = pd.DataFrame(data)
    features = ["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember", "EstimatedSalary", "Geography_Germany", "Geography_Spain", "Gender_Male"]
    res = preprocess_data(df, features, dummy_scaler)
    assert res.shape == (1, 11)

def test_preprocess_invalid_scaler():
    with pytest.raises(ValueError):
        preprocess_data(pd.DataFrame(), ["CreditScore"], None)

def test_preprocess_no_features(dummy_scaler):
    with pytest.raises(ValueError):
        preprocess_data(pd.DataFrame(), [], dummy_scaler)
