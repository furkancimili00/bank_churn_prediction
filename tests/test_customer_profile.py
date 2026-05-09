import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.customer_profile_service import (
    create_profile_card_fig,
    compute_customer_value_breakdown,
)

def test_create_profile_card_fig():
    """Müşteri profil kartı figürü oluşturulmalı."""
    customer = {
        "CreditScore": 700,
        "Age": 45,
        "Balance": 100000,
        "EstimatedSalary": 80000,
        "Tenure": 5,
        "NumOfProducts": 2,
        "IsActiveMember": 1,
        "HasCrCard": 1
    }
    fig = create_profile_card_fig(customer, 25.5, "Düşük")
    assert fig is not None
    assert "data" in fig

def test_compute_customer_value_breakdown():
    """Müşteri değeri grafik figürü oluşturulmalı."""
    customer = {"Balance": 50000, "EstimatedSalary": 60000, "NumOfProducts": 2}
    fig = compute_customer_value_breakdown(customer)
    assert fig is not None
    assert "data" in fig
