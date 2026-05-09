"""
Keşifsel Veri Analizi (EDA) servis modülü.
Dashboard'daki EDA sekmesi için veri analiz fonksiyonlarını barındırır.
Korelasyon, dağılım, box-plot ve çapraz analiz görselleştirmeleri üretir.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
from core.logging_config import get_logger

logger = get_logger(__name__)

# Analiz için kullanılacak sayısal sütunlar
NUMERIC_COLS = [
    "CreditScore", "Age", "Tenure", "Balance",
    "NumOfProducts", "EstimatedSalary",
]

# Kategorik sütunlar
CATEGORICAL_COLS = ["Geography", "Gender", "HasCrCard", "IsActiveMember"]


import streamlit as st

@st.cache_data
def load_default_dataset(filepath: str = "Churn_Modelling.csv") -> Optional[pd.DataFrame]:
    """
    Varsayılan veri setini yükler.

    Args:
        filepath (str): CSV dosyasının yolu.

    Returns:
        Optional[pd.DataFrame]: Yüklenen veri veya None.
    """
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Varsayılan veri seti yüklendi: {len(df)} satır")
        return df
    except FileNotFoundError:
        logger.warning(f"Veri seti bulunamadı: {filepath}")
        return None


def create_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Sayısal sütunlar arasındaki korelasyon ısı haritasını oluşturur.

    Args:
        df (pd.DataFrame): Analiz edilecek veri.

    Returns:
        go.Figure: Plotly ısı haritası figürü.
    """
    cols = [c for c in NUMERIC_COLS if c in df.columns]
    if "Exited" in df.columns:
        cols.append("Exited")

    corr_matrix = df[cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.columns.tolist(),
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 11},
        hovertemplate="<b>%{x}</b> ↔ <b>%{y}</b><br>Korelasyon: %{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        title="Özellikler Arası Korelasyon Matrisi",
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    logger.debug("Korelasyon ısı haritası oluşturuldu")
    return fig


def create_distribution_histograms(df: pd.DataFrame) -> go.Figure:
    """
    Sayısal sütunların dağılım histogramlarını oluşturur.
    Exited sütunu varsa churn/non-churn ayrımıyla gösterir.

    Args:
        df (pd.DataFrame): Analiz edilecek veri.

    Returns:
        go.Figure: Plotly histogram figürü (subplot'lu).
    """
    from plotly.subplots import make_subplots

    cols = [c for c in NUMERIC_COLS if c in df.columns]
    n_cols_grid = 3
    n_rows_grid = (len(cols) + n_cols_grid - 1) // n_cols_grid

    fig = make_subplots(
        rows=n_rows_grid, cols=n_cols_grid,
        subplot_titles=cols,
        vertical_spacing=0.08,
        horizontal_spacing=0.06,
    )

    has_exited = "Exited" in df.columns
    colors = {"Kalan": "#2ecc71", "Ayrılan": "#e74c3c"}

    for idx, col in enumerate(cols):
        row = idx // n_cols_grid + 1
        col_pos = idx % n_cols_grid + 1

        if has_exited:
            for label, exited_val, color in [("Kalan", 0, colors["Kalan"]), ("Ayrılan", 1, colors["Ayrılan"])]:
                subset = df[df["Exited"] == exited_val][col]
                fig.add_trace(
                    go.Histogram(
                        x=subset, name=label, marker_color=color,
                        opacity=0.7, showlegend=(idx == 0),
                    ),
                    row=row, col=col_pos,
                )
        else:
            fig.add_trace(
                go.Histogram(x=df[col], marker_color="#3498db", opacity=0.7, showlegend=False),
                row=row, col=col_pos,
            )

    fig.update_layout(
        title="Özellik Dağılımları (Churn Karşılaştırmalı)",
        barmode="overlay",
        height=300 * n_rows_grid,
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    logger.debug("Dağılım histogramları oluşturuldu")
    return fig


def create_churn_boxplots(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Churn vs Non-Churn karşılaştırmalı box-plot'lar oluşturur.

    Args:
        df (pd.DataFrame): Exited sütunu içeren veri.

    Returns:
        Optional[go.Figure]: Plotly box-plot figürü veya None.
    """
    if "Exited" not in df.columns:
        logger.warning("Exited sütunu bulunamadı, boxplot oluşturulamadı")
        return None

    from plotly.subplots import make_subplots

    cols = [c for c in NUMERIC_COLS if c in df.columns]
    n_cols_grid = 3
    n_rows_grid = (len(cols) + n_cols_grid - 1) // n_cols_grid

    fig = make_subplots(
        rows=n_rows_grid, cols=n_cols_grid,
        subplot_titles=cols,
        vertical_spacing=0.08,
    )

    df_plot = df.copy()
    df_plot["Durum"] = df_plot["Exited"].map({0: "Kalan", 1: "Ayrılan"})
    colors_map = {"Kalan": "#2ecc71", "Ayrılan": "#e74c3c"}

    for idx, col in enumerate(cols):
        row = idx // n_cols_grid + 1
        col_pos = idx % n_cols_grid + 1

        for durum, color in colors_map.items():
            subset = df_plot[df_plot["Durum"] == durum]
            fig.add_trace(
                go.Box(
                    y=subset[col], name=durum, marker_color=color,
                    showlegend=(idx == 0),
                ),
                row=row, col=col_pos,
            )

    fig.update_layout(
        title="Churn vs Non-Churn Karşılaştırması (Box Plot)",
        height=300 * n_rows_grid,
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    logger.debug("Boxplot grafikleri oluşturuldu")
    return fig


def create_categorical_analysis(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Coğrafya ve cinsiyet bazlı çapraz churn analizi (sunburst) oluşturur.

    Args:
        df (pd.DataFrame): Analiz edilecek veri.

    Returns:
        Optional[go.Figure]: Plotly sunburst figürü veya None.
    """
    if "Exited" not in df.columns:
        logger.warning("Exited sütunu bulunamadı, kategorik analiz oluşturulamadı")
        return None

    df_plot = df.copy()
    df_plot["Durum"] = df_plot["Exited"].map({0: "Kalan", 1: "Ayrılan"})

    fig = px.sunburst(
        df_plot,
        path=["Geography", "Gender", "Durum"],
        color="Durum",
        color_discrete_map={"Kalan": "#2ecc71", "Ayrılan": "#e74c3c"},
        title="Coğrafya → Cinsiyet → Churn Durumu (Sunburst)",
    )
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    logger.debug("Kategorik çapraz analiz (sunburst) oluşturuldu")
    return fig


def create_churn_rate_by_category(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Kategorik değişkenlere göre churn oranı bar grafiği oluşturur.

    Args:
        df (pd.DataFrame): Analiz edilecek veri.

    Returns:
        Optional[go.Figure]: Plotly bar chart figürü veya None.
    """
    if "Exited" not in df.columns:
        return None

    from plotly.subplots import make_subplots

    cats = [c for c in CATEGORICAL_COLS if c in df.columns]
    if not cats:
        return None

    fig = make_subplots(
        rows=1, cols=len(cats),
        subplot_titles=[f"Churn Oranı: {c}" for c in cats],
    )

    label_maps = {
        "HasCrCard": {0: "Yok", 1: "Var"},
        "IsActiveMember": {0: "Pasif", 1: "Aktif"},
    }

    for idx, cat in enumerate(cats):
        rates = df.groupby(cat)["Exited"].mean() * 100
        labels = [str(label_maps.get(cat, {}).get(k, k)) for k in rates.index]

        fig.add_trace(
            go.Bar(
                x=labels, y=rates.values,
                marker_color=["#e74c3c" if v > 20 else "#f39c12" if v > 15 else "#2ecc71" for v in rates.values],
                text=[f"%{v:.1f}" for v in rates.values],
                textposition="auto",
                showlegend=False,
            ),
            row=1, col=idx + 1,
        )

    fig.update_layout(
        title="Kategorik Değişkenlere Göre Churn Oranı (%)",
        height=400,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    logger.debug("Kategorik churn oranı grafiği oluşturuldu")
    return fig


def get_summary_statistics(df: pd.DataFrame) -> dict:
    """
    Veri seti için özet istatistikleri hesaplar.

    Args:
        df (pd.DataFrame): Analiz edilecek veri.

    Returns:
        dict: Toplam müşteri, ortalama yaş, churn oranı vb. metrikler.
    """
    stats = {
        "toplam_musteri": len(df),
        "ortalama_yas": round(df["Age"].mean(), 1) if "Age" in df.columns else None,
        "ortalama_bakiye": round(df["Balance"].mean(), 2) if "Balance" in df.columns else None,
        "ortalama_kredi_notu": round(df["CreditScore"].mean(), 1) if "CreditScore" in df.columns else None,
    }

    if "Exited" in df.columns:
        stats["churn_orani"] = round(df["Exited"].mean() * 100, 1)
        stats["churn_sayisi"] = int(df["Exited"].sum())
    else:
        stats["churn_orani"] = None
        stats["churn_sayisi"] = None

    logger.debug(f"Özet istatistikler hesaplandı: {stats['toplam_musteri']} müşteri")
    return stats
