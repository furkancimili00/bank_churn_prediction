"""
Veri Drift Tespiti (Data Drift Detection) servis modülü.
Yeni yüklenen verilerin eğitim verisi dağılımından sapmasını PSI ve KS testi ile ölçer.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from typing import Optional
from core.logging_config import get_logger

logger = get_logger(__name__)

# Drift eşik değerleri
PSI_THRESHOLD_WARNING = 0.10
PSI_THRESHOLD_CRITICAL = 0.25
KS_ALPHA = 0.05


def calculate_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """
    Population Stability Index (PSI) hesaplar.
    Eğitim ve yeni veri dağılımlarının ne kadar farklılaştığını ölçer.

    Args:
        expected (np.ndarray): Eğitim verisi (referans dağılım).
        actual (np.ndarray): Yeni veri (karşılaştırılacak dağılım).
        bins (int): Histogram kutusu sayısı.

    Returns:
        float: PSI değeri. 0'a yakınsa drift yok, >0.25 ise kritik drift.
    """
    # Ortak bin aralıkları oluştur
    breakpoints = np.linspace(
        min(expected.min(), actual.min()),
        max(expected.max(), actual.max()),
        bins + 1,
    )

    expected_counts = np.histogram(expected, bins=breakpoints)[0]
    actual_counts = np.histogram(actual, bins=breakpoints)[0]

    # Sıfır bölmeyi önle
    expected_pct = (expected_counts + 1) / (len(expected) + bins)
    actual_pct = (actual_counts + 1) / (len(actual) + bins)

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(round(psi, 6))


def run_ks_test(expected: np.ndarray, actual: np.ndarray) -> dict:
    """
    Kolmogorov-Smirnov testi uygular.

    Args:
        expected (np.ndarray): Referans dağılım.
        actual (np.ndarray): Karşılaştırılacak dağılım.

    Returns:
        dict: KS istatistiği, p-değeri ve drift tespiti.
    """
    ks_stat, p_value = stats.ks_2samp(expected, actual)
    return {
        "ks_statistic": round(ks_stat, 6),
        "p_value": round(p_value, 6),
        "drift_detected": p_value < KS_ALPHA,
    }


def analyze_drift(
    reference_df: pd.DataFrame, current_df: pd.DataFrame, numeric_cols: Optional[list[str]] = None
) -> list[dict]:
    """
    Referans ve güncel veri arasında her sayısal sütun için drift analizi yapar.

    Args:
        reference_df (pd.DataFrame): Eğitim/referans verisi.
        current_df (pd.DataFrame): Yeni yüklenen veri.
        numeric_cols (Optional[list[str]]): Analiz edilecek sütunlar.

    Returns:
        list[dict]: Her sütun için drift sonuçları.
    """
    if numeric_cols is None:
        numeric_cols = reference_df.select_dtypes(include=[np.number]).columns.tolist()
        # Hedef değişkeni ve ID'leri çıkar
        exclude = ["RowNumber", "CustomerId", "Exited"]
        numeric_cols = [c for c in numeric_cols if c not in exclude]

    common_cols = [c for c in numeric_cols if c in current_df.columns]
    results = []

    for col in common_cols:
        ref_vals = reference_df[col].dropna().values
        cur_vals = current_df[col].dropna().values

        if len(ref_vals) < 5 or len(cur_vals) < 5:
            continue

        psi = calculate_psi(ref_vals, cur_vals)
        ks = run_ks_test(ref_vals, cur_vals)

        severity = "✅ Normal"
        if psi >= PSI_THRESHOLD_CRITICAL:
            severity = "🔴 Kritik Drift"
        elif psi >= PSI_THRESHOLD_WARNING:
            severity = "🟡 Uyarı"

        results.append({
            "feature": col,
            "psi": psi,
            "ks_statistic": ks["ks_statistic"],
            "p_value": ks["p_value"],
            "ks_drift": ks["drift_detected"],
            "severity": severity,
            "ref_mean": round(float(ref_vals.mean()), 2),
            "cur_mean": round(float(cur_vals.mean()), 2),
            "mean_shift": round(float(cur_vals.mean() - ref_vals.mean()), 2),
        })

    logger.info(f"Drift analizi tamamlandı: {len(results)} özellik analiz edildi")
    return results


def create_drift_summary_table(drift_results: list[dict]) -> go.Figure:
    """
    Drift analiz sonuçlarını özet tablo olarak gösterir.

    Args:
        drift_results (list[dict]): Drift analiz sonuçları.

    Returns:
        go.Figure: Plotly tablo figürü.
    """
    if not drift_results:
        return go.Figure()

    headers = ["Özellik", "PSI", "KS İstatistiği", "p-Değeri", "Ort. Kayma", "Durum"]
    cells = [
        [r["feature"] for r in drift_results],
        [f"{r['psi']:.4f}" for r in drift_results],
        [f"{r['ks_statistic']:.4f}" for r in drift_results],
        [f"{r['p_value']:.4f}" for r in drift_results],
        [f"{r['mean_shift']:+.2f}" for r in drift_results],
        [r["severity"] for r in drift_results],
    ]

    # Renklendirme: drift varsa kırmızı
    row_colors = []
    for r in drift_results:
        if "Kritik" in r["severity"]:
            row_colors.append("#ffcccc")
        elif "Uyarı" in r["severity"]:
            row_colors.append("#fff3cd")
        else:
            row_colors.append("#d4edda")

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{h}</b>" for h in headers],
            fill_color="#2c3e50", font=dict(color="white", size=12),
            align="center",
        ),
        cells=dict(
            values=cells,
            fill_color=[row_colors] * len(headers),
            font=dict(size=11), align="center", height=28,
        ),
    )])
    fig.update_layout(
        title="📊 Veri Drift Analiz Raporu",
        height=50 + 35 * (len(drift_results) + 1),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def create_drift_distribution_fig(
    reference_df: pd.DataFrame, current_df: pd.DataFrame, feature: str
) -> go.Figure:
    """
    Referans ve güncel veri dağılımlarını üst üste histogram olarak gösterir.

    Args:
        reference_df (pd.DataFrame): Referans veri.
        current_df (pd.DataFrame): Güncel veri.
        feature (str): Karşılaştırılacak özellik adı.

    Returns:
        go.Figure: Histogram figürü.
    """
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=reference_df[feature].dropna(), name="Referans (Eğitim)",
        opacity=0.6, marker_color="#3498db",
    ))
    fig.add_trace(go.Histogram(
        x=current_df[feature].dropna(), name="Güncel Veri",
        opacity=0.6, marker_color="#e74c3c",
    ))
    fig.update_layout(
        title=f"{feature} — Dağılım Karşılaştırması",
        xaxis_title=feature, yaxis_title="Frekans",
        barmode="overlay", height=350,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig
