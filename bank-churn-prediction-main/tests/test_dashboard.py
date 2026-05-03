import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath('bank-churn-prediction-main'))

with patch('streamlit.cache_resource', lambda f: f), \
     patch('streamlit.set_page_config'), \
     patch('joblib.load') as mock_load:
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    mock_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 'Geography_Germany', 'Geography_Spain', 'Gender_Male']
    mock_load.return_value = {
        'model': mock_model,
        'scaler': mock_scaler,
        'features': mock_features
    }
    import dashboard

@pytest.fixture(autouse=True)
def setup_mocks():
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    mock_scaler.transform = MagicMock(side_effect=lambda x: x)

    mock_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 'Geography_Germany', 'Geography_Spain', 'Gender_Male']

    with patch('dashboard.local_model', mock_model), \
         patch('dashboard.local_scaler', mock_scaler), \
         patch('dashboard.expected_features', mock_features):
        yield mock_model, mock_scaler, mock_features

def test_make_prediction_high_risk(setup_mocks):
    mock_model, mock_scaler, mock_features = setup_mocks
    mock_model.predict_proba.return_value = np.array([[0.15, 0.85]])

    data_dict = {
        "CreditScore": 600, "Geography": "France", "Gender": "Female", "Age": 40,
        "Tenure": 3, "Balance": 60000, "NumOfProducts": 2,
        "HasCrCard": 1, "IsActiveMember": 0, "EstimatedSalary": 50000
    }

    result = dashboard.make_prediction(data_dict)

    assert result["churn_tahmini"] == 1
    assert result["churn_ihtimali"] == 0.85
    assert result["risk_seviyesi"] == "Yüksek"

def test_make_prediction_medium_risk(setup_mocks):
    mock_model, mock_scaler, mock_features = setup_mocks
    mock_model.predict_proba.return_value = np.array([[0.45, 0.55]])

    data_dict = {
        "CreditScore": 600, "Geography": "France", "Gender": "Female", "Age": 40,
        "Tenure": 3, "Balance": 60000, "NumOfProducts": 2,
        "HasCrCard": 1, "IsActiveMember": 0, "EstimatedSalary": 50000
    }

    result = dashboard.make_prediction(data_dict)

    assert result["churn_tahmini"] == 1
    assert result["churn_ihtimali"] == 0.55
    assert result["risk_seviyesi"] == "Orta"

def test_make_prediction_low_risk(setup_mocks):
    mock_model, mock_scaler, mock_features = setup_mocks
    mock_model.predict_proba.return_value = np.array([[0.80, 0.20]])

    data_dict = {
        "CreditScore": 600, "Geography": "France", "Gender": "Female", "Age": 40,
        "Tenure": 3, "Balance": 60000, "NumOfProducts": 2,
        "HasCrCard": 1, "IsActiveMember": 0, "EstimatedSalary": 50000
    }

    result = dashboard.make_prediction(data_dict)

    assert result["churn_tahmini"] == 0
    assert result["churn_ihtimali"] == 0.20
    assert result["risk_seviyesi"] == "Düşük"

def test_make_prediction_dataframe_transformation(setup_mocks):
    mock_model, mock_scaler, mock_features = setup_mocks
    mock_model.predict_proba.return_value = np.array([[0.9, 0.1]])

    data_dict = {
        "CreditScore": 650,
        "Geography": "Germany",
        "Gender": "Male",
        "Age": 40,
        "Tenure": 5,
        "Balance": 50000,
        "NumOfProducts": 1,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 60000
    }

    dashboard.make_prediction(data_dict)

    mock_scaler.transform.assert_called_once()

    call_args = mock_scaler.transform.call_args[0]
    df_transformed = call_args[0]

    assert list(df_transformed.columns) == mock_features
    # Check that missing columns were correctly initialized to 0
    # Because there's only one row, "Geography_Spain" doesn't appear in get_dummies output
    # but gets added by the padding loop as 0
    assert df_transformed['Geography_Spain'].iloc[0] == 0
