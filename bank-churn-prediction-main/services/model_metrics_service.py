"""
Model Performans İzleme servis modülü.
Eğitilmiş modelin başarı metriklerini hesaplar ve görselleştirir.
Confusion Matrix, ROC Eğrisi, Precision-Recall Eğrisi ve Feature Importance içerir.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
    f1_score,
    accuracy_score,
    precision_score,
    recall_score,
)
from typing import Optional, Any, List, Dict
from core.logging_config import get_logger

logger = get_logger(__name__)

# THESIS_CONTEXT.md'den gelen hedef metrikler
THESIS_TARGETS = {
    "F1-Score": 0.85,
    "ROC-AUC": 0.90,
    "API Yanıt Süresi (s)": 1.0,
    "Disparate Impact": 1.2,
}


def compute_all_metrics(
    model: Any, scaler: Any, features: List[str], df: pd.DataFrame
) -> Optional[Dict[str, Any]]:
    """
    Model üzerinde tüm performans metriklerini hesaplar.

    Args:
        model: Eğitilmiş model objesi.
        scaler: StandardScaler objesi.
        features (list): Modelin beklediği özellik listesi.
        df (pd.DataFrame): Exited sütunu içeren veri seti.

    Returns:
        Optional[dict]: Tahmin, olasılık ve metrik değerlerini içeren sözlük.
    """
    if "Exited" not in df.columns:
        logger.warning("Veri setinde 'Exited' sütunu bulunamadı")
        return None

    try:
        from core.utils import preprocess_data

        X = df.drop(columns=["RowNumber", "CustomerId", "Surname", "Exited"], errors="ignore")
        y_true = df["Exited"].values

        X_processed = preprocess_data(X, features, scaler)

        y_pred = model.predict(X_processed)
        y_proba = model.predict_proba(X_processed)[:, 1]

        metrics = {
            "y_true": y_true,
            "y_pred": y_pred,
            "y_proba": y_proba,
            "accuracy": accuracy_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "roc_auc": roc_auc_score(y_true, y_proba),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
        }
        logger.info(
            f"Model metrikleri hesaplandı — F1: {metrics['f1']:.4f}, "
            f"ROC-AUC: {metrics['roc_auc']:.4f}"
        )
        return metrics
    except Exception as e:
        logger.error(f"Metrik hesaplama hatası: {e}")
        return None


def create_confusion_matrix_fig(y_true: np.ndarray, y_pred: np.ndarray) -> go.Figure:
    """
    Confusion Matrix ısı haritası oluşturur.

    Args:
        y_true: Gerçek etiketler.
        y_pred: Tahmin edilen etiketler.

    Returns:
        go.Figure: Plotly heatmap figürü.
    """
    cm = confusion_matrix(y_true, y_pred)
    labels = ["Kalan (0)", "Ayrılan (1)"]

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=labels, y=labels,
        colorscale="Blues",
        text=cm, texttemplate="%{text}",
        textfont={"size": 18},
        hovertemplate="Gerçek: %{y}<br>Tahmin: %{x}<br>Sayı: %{z}<extra></extra>",
    ))
    fig.update_layout(
        title="Karışıklık Matrisi (Confusion Matrix)",
        xaxis_title="Tahmin Edilen", yaxis_title="Gerçek Değer",
        height=400, margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def create_roc_curve_fig(y_true: np.ndarray, y_proba: np.ndarray) -> go.Figure:
    """
    ROC eğrisi ve AUC skoru grafiği oluşturur.

    Args:
        y_true: Gerçek etiketler.
        y_proba: Tahmin olasılıkları.

    Returns:
        go.Figure: Plotly ROC eğrisi figürü.
    """
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    auc_val = roc_auc_score(y_true, y_proba)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr, mode="lines",
        name=f"ROC Eğrisi (AUC = {auc_val:.4f})",
        line=dict(color="#3498db", width=2.5),
        fill="tozeroy", fillcolor="rgba(52, 152, 219, 0.1)",
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        name="Rastgele Sınıflandırıcı",
        line=dict(color="gray", dash="dash"),
    ))
    # Hedef çizgisi
    fig.add_hline(
        y=THESIS_TARGETS["ROC-AUC"], line_dash="dot",
        line_color="#e74c3c", annotation_text=f"Tez Hedefi: {THESIS_TARGETS['ROC-AUC']}",
    )
    fig.update_layout(
        title=f"ROC Eğrisi (AUC = {auc_val:.4f})",
        xaxis_title="Yanlış Pozitif Oranı (FPR)",
        yaxis_title="Doğru Pozitif Oranı (TPR)",
        height=450, margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(x=0.5, y=0.05),
    )
    return fig


def create_precision_recall_fig(y_true: np.ndarray, y_proba: np.ndarray) -> go.Figure:
    """
    Precision-Recall eğrisi oluşturur.

    Args:
        y_true: Gerçek etiketler.
        y_proba: Tahmin olasılıkları.

    Returns:
        go.Figure: Plotly PR eğrisi figürü.
    """
    precision_vals, recall_vals, _ = precision_recall_curve(y_true, y_proba)
    ap = average_precision_score(y_true, y_proba)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recall_vals, y=precision_vals, mode="lines",
        name=f"PR Eğrisi (AP = {ap:.4f})",
        line=dict(color="#e67e22", width=2.5),
        fill="tozeroy", fillcolor="rgba(230, 126, 34, 0.1)",
    ))
    fig.update_layout(
        title=f"Precision-Recall Eğrisi (AP = {ap:.4f})",
        xaxis_title="Recall (Duyarlılık)",
        yaxis_title="Precision (Kesinlik)",
        height=450, margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def create_feature_importance_fig(model, features: list) -> Optional[go.Figure]:
    """
    Model özellik önem sıralaması (Feature Importance) bar chart'ı oluşturur.

    Args:
        model: Eğitilmiş model objesi (feature_importances_ desteği olmalı).
        features (list): Özellik adları listesi.

    Returns:
        Optional[go.Figure]: Plotly bar chart figürü veya None.
    """
    try:
        importances = model.feature_importances_
    except AttributeError:
        logger.warning("Model feature_importances_ desteklemiyor")
        return None

    sort_idx = np.argsort(importances)
    sorted_features = np.array(features)[sort_idx]
    sorted_importances = importances[sort_idx]

    colors = [f"rgba(52, 152, 219, {0.3 + 0.7 * (i / len(sort_idx))})" for i in range(len(sort_idx))]

    fig = go.Figure(go.Bar(
        x=sorted_importances, y=sorted_features,
        orientation="h", marker_color=colors,
        text=[f"{v:.4f}" for v in sorted_importances],
        textposition="auto",
    ))
    fig.update_layout(
        title="Özellik Önem Sıralaması (Feature Importance)",
        xaxis_title="Önem Değeri",
        height=450, margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def create_metrics_comparison_table(metrics: dict) -> go.Figure:
    """
    Mevcut model metriklerini tez hedefleriyle karşılaştıran tablo oluşturur.

    Args:
        metrics (dict): compute_all_metrics fonksiyonundan dönen metrik sözlüğü.

    Returns:
        go.Figure: Plotly tablo figürü.
    """
    rows = [
        ["Doğruluk (Accuracy)", f"{metrics['accuracy']:.4f}", "—", "ℹ️"],
        ["F1-Score", f"{metrics['f1']:.4f}", f"> {THESIS_TARGETS['F1-Score']}", "✅" if metrics["f1"] > THESIS_TARGETS["F1-Score"] else "❌"],
        ["ROC-AUC", f"{metrics['roc_auc']:.4f}", f"> {THESIS_TARGETS['ROC-AUC']}", "✅" if metrics["roc_auc"] > THESIS_TARGETS["ROC-AUC"] else "❌"],
        ["Kesinlik (Precision)", f"{metrics['precision']:.4f}", "—", "ℹ️"],
        ["Duyarlılık (Recall)", f"{metrics['recall']:.4f}", "—", "ℹ️"],
    ]

    header_vals = ["Metrik", "Mevcut Değer", "Tez Hedefi", "Durum"]
    cell_vals = list(zip(*rows))

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{h}</b>" for h in header_vals],
            fill_color="#2c3e50", font=dict(color="white", size=13),
            align="center",
        ),
        cells=dict(
            values=cell_vals,
            fill_color=[["#ecf0f1"] * len(rows)],
            font=dict(color="black", size=12), align="center", height=30,
        ),
    )])
    fig.update_layout(
        title="Model Metrikleri — Tez Hedefleri Karşılaştırması",
        height=280, margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig
