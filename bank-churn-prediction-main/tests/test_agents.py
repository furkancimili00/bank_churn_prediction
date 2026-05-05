import sys
import os
import pytest

# Proje ana dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import run_agent

def test_agent_high_risk():
    """
    Yüksek riskli müşteri (%75) için 'Acil İletişim & %20 İndirim Maili Gönder'
    aksiyonunun önerildiğini test eder.
    """
    result = run_agent(customer_id="TEST-001", churn_probability=0.75, risk_level="Yüksek")
    assert result["recommended_action"] == "Acil İletişim & %20 İndirim Maili Gönder"

def test_agent_medium_risk():
    """
    Orta riskli müşteri (%50) için 'Kredi Kartı Kampanyası Öner'
    aksiyonunun önerildiğini test eder.
    """
    result = run_agent(customer_id="TEST-002", churn_probability=0.50, risk_level="Orta")
    assert result["recommended_action"] == "Kredi Kartı Kampanyası Öner"

def test_agent_low_risk():
    """
    Düşük riskli müşteri (%20) için 'İşlem Yok (Sadık Müşteri)'
    aksiyonunun önerildiğini test eder.
    """
    result = run_agent(customer_id="TEST-003", churn_probability=0.20, risk_level="Düşük")
    assert result["recommended_action"] == "İşlem Yok (Sadık Müşteri)"
