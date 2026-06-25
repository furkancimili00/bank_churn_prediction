import pytest
from unittest.mock import MagicMock
import pandas as pd
import sys
import os

# Add parent directory to path to import dashboard
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dashboard

def test_main_dashboard_renders(mocker):
    # Mock streamlit functions
    mocker.patch('dashboard.st.sidebar.title')
    mocker.patch('dashboard.st.sidebar.info')
    mocker.patch('dashboard.st.sidebar.button', return_value=False)
    mocker.patch('dashboard.st.title')

    # Mock tabs
    mock_tab1 = MagicMock()
    mock_tab1.__enter__ = MagicMock(return_value=mock_tab1)
    mock_tab1.__exit__ = MagicMock(return_value=None)
    mock_tab2 = MagicMock()
    mock_tab2.__enter__ = MagicMock(return_value=mock_tab2)
    mock_tab2.__exit__ = MagicMock(return_value=None)
    mock_tab3 = MagicMock()
    mock_tab3.__enter__ = MagicMock(return_value=mock_tab3)
    mock_tab3.__exit__ = MagicMock(return_value=None)

    mocker.patch('dashboard.st.tabs', return_value=[mock_tab1, mock_tab2, mock_tab3])

    # Mock other layout elements and widgets that are inside the tabs
    mocker.patch('dashboard.st.subheader')

    # Generic side effect to handle st.columns with varying number of columns
    def columns_side_effect(num_cols):
        return [MagicMock() for _ in range(num_cols)]
    mocker.patch('dashboard.st.columns', side_effect=columns_side_effect)

    mocker.patch('dashboard.st.number_input')
    mocker.patch('dashboard.st.selectbox')
    mocker.patch('dashboard.st.button', return_value=False)
    mocker.patch('dashboard.st.warning')
    mocker.patch('dashboard.st.file_uploader', return_value=None)

    # Setup session state using mocker
    mock_session_state = MagicMock()
    mock_session_state.current_customer = None
    mocker.patch('dashboard.st.session_state', new=mock_session_state)

    # Call the function
    dashboard.main_dashboard()

    # Verify calls
    dashboard.st.sidebar.title.assert_any_call("Yönetici Menüsü")
    dashboard.st.sidebar.button.assert_any_call("🚪 Güvenli Çıkış Yap")
    dashboard.st.title.assert_any_call("🏦 Şube Müdürü Müşteri Risk Analiz Paneli")
    dashboard.st.tabs.assert_any_call(["👤 Tekil Müşteri Analizi", "🧪 What-If Simülatörü", "📂 Toplu Analiz (CLTV Öncelikli)"])

def test_main_dashboard_logout(mocker):
    # Mock streamlit functions
    mocker.patch('dashboard.st.sidebar.title')
    mocker.patch('dashboard.st.sidebar.info')

    def button_side_effect(text, **kwargs):
        if text == "🚪 Güvenli Çıkış Yap":
            return True
        return False

    mocker.patch('dashboard.st.sidebar.button', side_effect=button_side_effect)
    mocker.patch('dashboard.st.rerun')
    mocker.patch('dashboard.st.title')

    # Mock tabs
    mock_tab1 = MagicMock()
    mock_tab1.__enter__ = MagicMock(return_value=mock_tab1)
    mock_tab1.__exit__ = MagicMock(return_value=None)
    mock_tab2 = MagicMock()
    mock_tab2.__enter__ = MagicMock(return_value=mock_tab2)
    mock_tab2.__exit__ = MagicMock(return_value=None)
    mock_tab3 = MagicMock()
    mock_tab3.__enter__ = MagicMock(return_value=mock_tab3)
    mock_tab3.__exit__ = MagicMock(return_value=None)

    mocker.patch('dashboard.st.tabs', return_value=[mock_tab1, mock_tab2, mock_tab3])

    # Mock other layout elements
    mocker.patch('dashboard.st.subheader')

    # Generic side effect to handle st.columns with varying number of columns
    def columns_side_effect(num_cols):
        return [MagicMock() for _ in range(num_cols)]
    mocker.patch('dashboard.st.columns', side_effect=columns_side_effect)

    mocker.patch('dashboard.st.number_input')
    mocker.patch('dashboard.st.selectbox')
    mocker.patch('dashboard.st.button', return_value=False)
    mocker.patch('dashboard.st.warning')
    mocker.patch('dashboard.st.file_uploader', return_value=None)

    # Set session state using mocker
    mock_session_state = MagicMock()
    mock_session_state.logged_in = True
    mock_session_state.current_customer = None
    mocker.patch('dashboard.st.session_state', new=mock_session_state)

    # Call the function
    dashboard.main_dashboard()

    # Verify logout effects
    dashboard.st.sidebar.button.assert_any_call("🚪 Güvenli Çıkış Yap")
    assert dashboard.st.session_state.logged_in is False
    dashboard.st.rerun.assert_called_once()
