import pytest
import sys
from unittest.mock import MagicMock, patch

# In this environment, libraries like pandas, numpy, and streamlit are NOT INSTALLED.
# So we MUST MOCK THEM. However, we should mock them locally for this test
# and clean up sys.modules afterwards to prevent pollution.

@pytest.fixture(autouse=True)
def mock_all_deps():
    """Mock all heavy dependencies to prevent them from running during tests and clean up after."""
    # Keep original sys.modules to restore later
    original_modules = sys.modules.copy()

    # Create mocks
    st_mock = MagicMock()
    st_mock.cache_resource = lambda func: func
    st_mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    st_mock.session_state = MagicMock()
    st_mock.session_state.logged_in = False
    st_mock.secrets = {"auth": {"username": "admin", "password": "password"}}

    # Mock everything missing in environment
    sys.modules['streamlit'] = st_mock
    sys.modules['plotly'] = MagicMock()
    sys.modules['plotly.graph_objects'] = MagicMock()
    sys.modules['shap'] = MagicMock()

    # Mocks for data processing
    pd_mock = MagicMock()
    sys.modules['pandas'] = pd_mock

    np_mock = MagicMock()
    sys.modules['numpy'] = np_mock

    # Mock joblib
    joblib_mock = MagicMock()
    sys.modules['joblib'] = joblib_mock

    yield

    # Restore original modules
    sys.modules.clear()
    sys.modules.update(original_modules)

@pytest.fixture
def mock_model_artifacts():
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    # Mocking standard features structure for dummy data
    mock_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts',
                     'HasCrCard', 'IsActiveMember', 'EstimatedSalary',
                     'Geography_Germany', 'Geography_Spain', 'Gender_Male']

    return mock_model, mock_scaler, mock_features


def test_load_local_model_success(mock_all_deps, mock_model_artifacts):
    """Test that model loading works correctly."""
    import dashboard
    import joblib

    mock_model, mock_scaler, mock_features = mock_model_artifacts

    mock_joblib_data = {
        'model': mock_model,
        'scaler': mock_scaler,
        'features': mock_features
    }

    joblib.load.return_value = mock_joblib_data

    model, scaler, features = dashboard.load_local_model()
    assert model == mock_model
    assert scaler == mock_scaler
    assert features == mock_features

def test_load_local_model_failure(mock_all_deps):
    """Test model loading failure."""
    import dashboard
    import joblib

    joblib.load.side_effect = Exception("File not found")

    model, scaler, features = dashboard.load_local_model()
    assert model is None
    assert scaler is None
    assert features is None

def test_make_prediction_high_risk(mock_all_deps, mock_model_artifacts):
    """Test make_prediction with a high risk outcome using mocked data libraries."""
    import dashboard
    import pandas as pd

    mock_model, mock_scaler, mock_features = mock_model_artifacts

    # Set up dashboard with mocked artifacts
    dashboard.expected_features = mock_features
    dashboard.local_model = mock_model
    dashboard.local_scaler = mock_scaler

    customer_data = {"dummy": "data"}

    # Mock pandas behaviors used in make_prediction
    df_mock = MagicMock()
    df_mock.columns = mock_features
    df_mock.__getitem__.return_value = df_mock
    pd.get_dummies.return_value = df_mock
    pd.DataFrame.return_value = df_mock

    # Mock the return from predict_proba
    # predict_proba returns a 2D array, we slice it [0][1] in code
    dashboard.local_model.predict_proba.return_value = [[0.2, 0.8]]

    result = dashboard.make_prediction(customer_data)

    assert result["churn_tahmini"] == 1
    assert result["churn_ihtimali"] == 0.8
    assert result["risk_seviyesi"] == "Yüksek"

def test_make_prediction_low_risk(mock_all_deps, mock_model_artifacts):
    """Test make_prediction with a low risk outcome using mocked data libraries."""
    import dashboard
    import pandas as pd

    mock_model, mock_scaler, mock_features = mock_model_artifacts

    dashboard.expected_features = mock_features
    dashboard.local_model = mock_model
    dashboard.local_scaler = mock_scaler

    customer_data = {"dummy": "data"}

    df_mock = MagicMock()
    df_mock.columns = mock_features
    df_mock.__getitem__.return_value = df_mock
    pd.get_dummies.return_value = df_mock
    pd.DataFrame.return_value = df_mock

    dashboard.local_model.predict_proba.return_value = [[0.7, 0.3]]

    result = dashboard.make_prediction(customer_data)

    assert result["churn_tahmini"] == 0
    assert result["churn_ihtimali"] == 0.3
    assert result["risk_seviyesi"] == "Düşük"
