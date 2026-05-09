"""
Müşteri Segmentasyonu servis modülü.
K-Means kümeleme, PCA boyut indirgeme ve segment profil analizi fonksiyonlarını barındırır.
Dashboard'daki Segmentasyon sekmesi için kullanılır.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Optional
from core.logging_config import get_logger

logger = get_logger(__name__)

# Segmentasyon için kullanılacak sayısal özellikler
SEGMENT_FEATURES = [
    "CreditScore", "Age", "Tenure", "Balance",
    "NumOfProducts", "EstimatedSalary",
]


import streamlit as st

@st.cache_data
def find_optimal_k(df: pd.DataFrame, max_k: int = 8) -> go.Figure:
    """
    Elbow Method ile optimum küme sayısını belirlemek için inertia grafiği oluşturur.

    Args:
        df (pd.DataFrame): Kümelenecek veri.
        max_k (int): Denenecek maksimum küme sayısı.

    Returns:
        go.Figure: Elbow grafiği.
    """
    cols = [c for c in SEGMENT_FEATURES if c in df.columns]
    X = df[cols].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    inertias = []
    k_range = range(2, max_k + 1)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(k_range), y=inertias,
        mode="lines+markers",
        marker=dict(size=10, color="#3498db"),
        line=dict(width=2.5, color="#3498db"),
        name="Inertia",
    ))
    fig.update_layout(
        title="Elbow Method — Optimum Küme Sayısı Seçimi",
        xaxis_title="Küme Sayısı (k)",
        yaxis_title="Inertia (Toplam Küme İçi Mesafe)",
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    logger.debug("Elbow grafiği oluşturuldu")
    return fig


@st.cache_data
def perform_segmentation(
    df: pd.DataFrame, n_clusters: int = 3
) -> tuple[pd.DataFrame, np.ndarray, StandardScaler]:
    """
    K-Means kümeleme uygular ve segment etiketlerini veri setine ekler.

    Args:
        df (pd.DataFrame): Kümelenecek veri.
        n_clusters (int): Küme sayısı.

    Returns:
        tuple: (Segment eklenmiş DataFrame, ölçeklenmiş veri, scaler objesi)
    """
    cols = [c for c in SEGMENT_FEATURES if c in df.columns]
    X = df[cols].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    df_result = df.copy()
    df_result["Segment"] = labels
    df_result["Segment_Adi"] = df_result["Segment"].apply(
        lambda x: f"Segment {x + 1}"
    )

    logger.info(f"Segmentasyon tamamlandı: {n_clusters} küme, {len(df)} müşteri")
    return df_result, X_scaled, scaler


def create_pca_scatter(
    df_segmented: pd.DataFrame, X_scaled: np.ndarray
) -> go.Figure:
    """
    PCA ile 2 boyuta indirgenmiş kümeleme görselleştirmesi oluşturur.

    Args:
        df_segmented (pd.DataFrame): Segment etiketli veri.
        X_scaled (np.ndarray): Ölçeklenmiş özellik matrisi.

    Returns:
        go.Figure: 2D PCA scatter plot.
    """
    pca = PCA(n_components=2, random_state=42)
    components = pca.fit_transform(X_scaled)

    df_plot = pd.DataFrame({
        "PC1": components[:, 0],
        "PC2": components[:, 1],
        "Segment": df_segmented["Segment_Adi"].values,
    })

    colors = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22", "#34495e"]

    fig = px.scatter(
        df_plot, x="PC1", y="PC2", color="Segment",
        color_discrete_sequence=colors,
        title=f"PCA Kümeleme Görselleştirmesi (Açıklanan Varyans: %{pca.explained_variance_ratio_.sum()*100:.1f})",
        hover_data={"PC1": ":.2f", "PC2": ":.2f"},
    )
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    fig.update_traces(marker=dict(size=5, opacity=0.7))
    logger.debug("PCA scatter plot oluşturuldu")
    return fig


def create_segment_profile(df_segmented: pd.DataFrame) -> go.Figure:
    """
    Her segment için ortalama özellik değerlerini gösteren radar grafiği oluşturur.

    Args:
        df_segmented (pd.DataFrame): Segment etiketli veri.

    Returns:
        go.Figure: Radar (polar) grafik.
    """
    cols = [c for c in SEGMENT_FEATURES if c in df_segmented.columns]
    segment_means = df_segmented.groupby("Segment_Adi")[cols].mean()

    # Normalize (0-1 arası) karşılaştırma için
    normalized = (segment_means - segment_means.min()) / (segment_means.max() - segment_means.min() + 1e-8)

    colors = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12", "#9b59b6", "#1abc9c"]
    fig = go.Figure()

    for idx, (segment, row) in enumerate(normalized.iterrows()):
        fig.add_trace(go.Scatterpolar(
            r=row.values.tolist() + [row.values[0]],
            theta=cols + [cols[0]],
            fill="toself",
            name=segment,
            line_color=colors[idx % len(colors)],
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Segment Profilleri (Normalize Edilmiş Radar Grafik)",
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    logger.debug("Segment radar grafiği oluşturuldu")
    return fig


def create_segment_summary_table(df_segmented: pd.DataFrame) -> go.Figure:
    """
    Her segment için özet istatistikleri tablo olarak gösterir.

    Args:
        df_segmented (pd.DataFrame): Segment etiketli veri.

    Returns:
        go.Figure: Plotly tablo figürü.
    """
    summary_rows = []
    for segment in sorted(df_segmented["Segment_Adi"].unique()):
        seg_data = df_segmented[df_segmented["Segment_Adi"] == segment]
        row = {
            "Segment": segment,
            "Müşteri Sayısı": len(seg_data),
            "Ort. Yaş": round(seg_data["Age"].mean(), 1) if "Age" in seg_data.columns else "—",
            "Ort. Bakiye (€)": f"{seg_data['Balance'].mean():,.0f}" if "Balance" in seg_data.columns else "—",
            "Ort. Kredi Notu": round(seg_data["CreditScore"].mean(), 0) if "CreditScore" in seg_data.columns else "—",
            "Ort. Ürün Sayısı": round(seg_data["NumOfProducts"].mean(), 1) if "NumOfProducts" in seg_data.columns else "—",
        }
        if "Exited" in seg_data.columns:
            row["Churn Oranı (%)"] = f"{seg_data['Exited'].mean() * 100:.1f}"
        summary_rows.append(row)

    df_summary = pd.DataFrame(summary_rows)
    headers = list(df_summary.columns)
    cell_vals = [df_summary[col].tolist() for col in headers]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{h}</b>" for h in headers],
            fill_color="#2c3e50", font=dict(color="white", size=12),
            align="center",
        ),
        cells=dict(
            values=cell_vals,
            fill_color=[["#ecf0f1"] * len(summary_rows)],
            font=dict(color="black", size=11), align="center", height=28,
        ),
    )])
    fig.update_layout(
        title="Segment Özet Tablosu",
        height=50 + 35 * (len(summary_rows) + 1),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    logger.debug("Segment özet tablosu oluşturuldu")
    return fig


def create_segment_churn_bar(df_segmented: pd.DataFrame) -> Optional[go.Figure]:
    """
    Segment bazlı churn oranı bar grafiği oluşturur.

    Args:
        df_segmented (pd.DataFrame): Segment etiketli, Exited sütunlu veri.

    Returns:
        Optional[go.Figure]: Bar chart veya None.
    """
    if "Exited" not in df_segmented.columns:
        return None

    churn_rates = df_segmented.groupby("Segment_Adi")["Exited"].mean() * 100
    churn_rates = churn_rates.sort_values(ascending=False)

    colors = ["#e74c3c" if v > 25 else "#f39c12" if v > 15 else "#2ecc71" for v in churn_rates.values]

    fig = go.Figure(go.Bar(
        x=churn_rates.index.tolist(),
        y=churn_rates.values,
        marker_color=colors,
        text=[f"%{v:.1f}" for v in churn_rates.values],
        textposition="auto",
    ))
    fig.update_layout(
        title="Segment Bazlı Churn Oranı (%)",
        xaxis_title="Segment", yaxis_title="Churn Oranı (%)",
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    logger.debug("Segment churn bar grafiği oluşturuldu")
    return fig
