"""
Yeni servis modüllerinin birim testleri.
drift_service, data_privacy ve audit_service fonksiyonlarını test eder.
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestDriftService:
    """Drift tespiti servis testleri."""

    def test_calculate_psi_identical(self):
        """Aynı dağılımlar için PSI sıfıra yakın olmalı."""
        from services.drift_service import calculate_psi
        data = np.random.normal(0, 1, 1000)
        psi = calculate_psi(data, data)
        assert psi < 0.01

    def test_calculate_psi_different(self):
        """Farklı dağılımlar için PSI yüksek olmalı."""
        from services.drift_service import calculate_psi
        ref = np.random.normal(0, 1, 1000)
        cur = np.random.normal(5, 1, 1000)
        psi = calculate_psi(ref, cur)
        assert psi > 0.1

    def test_run_ks_test_same(self):
        """Aynı dağılım için KS testi drift tespit etmemeli."""
        from services.drift_service import run_ks_test
        data = np.random.normal(0, 1, 500)
        result = run_ks_test(data, data)
        assert result["drift_detected"] == False  # noqa: E712 — numpy bool_ uyumu

    def test_analyze_drift_returns_results(self):
        """analyze_drift geçerli sonuçlar döndürmeli."""
        from services.drift_service import analyze_drift
        ref = pd.DataFrame({"Age": np.random.normal(40, 10, 100), "Balance": np.random.normal(50000, 10000, 100)})
        cur = pd.DataFrame({"Age": np.random.normal(42, 10, 80), "Balance": np.random.normal(50000, 10000, 80)})
        results = analyze_drift(ref, cur, numeric_cols=["Age", "Balance"])
        assert len(results) == 2
        assert all("psi" in r for r in results)


class TestDataPrivacy:
    """Veri gizliliği servis testleri."""

    def test_detect_pii_columns(self):
        """PII sütunları doğru tespit edilmeli."""
        from services.data_privacy import detect_pii_columns
        df = pd.DataFrame({"Surname": ["A"], "CustomerId": [1], "Age": [30]})
        pii = detect_pii_columns(df)
        assert "Surname" in pii
        assert "CustomerId" in pii
        assert "Age" not in pii

    def test_anonymize_hash(self):
        """Hash maskeleme sonrası değerler değişmeli."""
        from services.data_privacy import anonymize_dataframe
        df = pd.DataFrame({"Surname": ["Yılmaz", "Demir"], "Age": [30, 40]})
        result = anonymize_dataframe(df, method="hash")
        assert result["Surname"].iloc[0] != "Yılmaz"
        assert result["Age"].iloc[0] == 30  # Sayısal değer korunmalı

    def test_anonymize_redact(self):
        """Redact maskeleme [GİZLİ] olmalı."""
        from services.data_privacy import anonymize_dataframe
        df = pd.DataFrame({"Surname": ["Test"], "Age": [25]})
        result = anonymize_dataframe(df, method="redact")
        assert result["Surname"].iloc[0] == "[GİZLİ]"

    def test_privacy_report(self):
        """Gizlilik raporu doğru bilgi döndürmeli."""
        from services.data_privacy import generate_privacy_report, anonymize_dataframe
        df = pd.DataFrame({"Surname": ["A"], "CustomerId": [1], "Balance": [100]})
        anon = anonymize_dataframe(df)
        report = generate_privacy_report(df, anon)
        assert report["maskelenen_sutun_sayisi"] >= 2
        assert report["toplam_satir"] == 1


class TestAuditService:
    """Denetim günlüğü servis testleri."""

    def test_log_event_and_read(self, tmp_path, monkeypatch):
        """Olay kaydedilip okunabilmeli."""
        import services.audit_service as audit_service
        log_file = str(tmp_path / "test_audit.jsonl")
        monkeypatch.setattr(audit_service, "AUDIT_LOG_FILE", log_file)

        from services.audit_service import log_event, get_recent_events
        log_event("test_event", {"key": "value"})
        events = get_recent_events(limit=10)
        assert len(events) >= 1
        assert events[0]["event_type"] == "test_event"

    def test_event_summary(self, tmp_path, monkeypatch):
        """Olay özeti doğru hesaplanmalı."""
        import services.audit_service as audit_service
        log_file = str(tmp_path / "test_summary.jsonl")
        monkeypatch.setattr(audit_service, "AUDIT_LOG_FILE", log_file)

        from services.audit_service import log_event, get_event_summary
        log_event("login")
        log_event("predict")
        log_event("predict")
        summary = get_event_summary()
        assert summary["toplam_kayit"] == 3
        assert summary["olay_tipleri"]["predict"] == 2

    def test_clear_log(self, tmp_path, monkeypatch):
        """Log temizleme başarılı olmalı."""
        import services.audit_service as audit_service
        log_file = str(tmp_path / "test_clear.jsonl")
        monkeypatch.setattr(audit_service, "AUDIT_LOG_FILE", log_file)

        from services.audit_service import log_event, clear_audit_log, get_recent_events
        log_event("test")
        clear_audit_log()
        events = get_recent_events()
        assert len(events) == 0
