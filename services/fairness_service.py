"""
Adillik ve Önyargı (Fairness/Bias) analiz servis modülü.
Modelin cinsiyet ve coğrafya bazında adil tahmin yapıp yapmadığını ölçer.
THESIS_CONTEXT.md'deki disparate impact < 1.2 hedefini doğrular.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional
from core.logging_config import get_logger

logger = get_logger(__name__)

# Tez hedefi
DISPARATE_IMPACT_THRESHOLD = 1.2


def compute_group_churn_rates(
    df: pd.DataFrame, model, scaler, features: list, group_col: str
) -> Optional[pd.DataFrame]:
    """
    Belirli bir kategorik sütuna göre grupların churn oranlarını hesaplar.

    Args:
        df (pd.DataFrame): Ham veri seti.
        model: Eğitilmiş model objesi.
        scaler: StandardScaler objesi.
        features (list): Model özellikleri listesi.
        group_col (str): Gruplama yapılacak sütun adı (ör. 'Gender', 'Geography').

    Returns:
        Optional[pd.DataFrame]: Grup bazlı churn oranları veya None.
    """
    if group_col not in df.columns:
        logger.warning(f"Sütun bulunamadı: {group_col}")
        return None

    try:
        from core.utils import preprocess_data

        X = df.drop(columns=["RowNumber", "CustomerId", "Surname", "Exited"], errors="ignore")
        X_processed = preprocess_data(X, features, scaler)
        y_proba = model.predict_proba(X_processed)[:, 1]
        y_pred = (y_proba > 0.5).astype(int)

        df_result = df[[group_col]].copy()
        df_result["Churn_Pred"] = y_pred
        df_result["Churn_Proba"] = y_proba

        if "Exited" in df.columns:
            df_result["Gercek_Churn"] = df["Exited"].values

        group_stats = df_result.groupby(group_col).agg(
            Musteri_Sayisi=("Churn_Pred", "count"),
            Tahmin_Churn_Orani=("Churn_Pred", "mean"),
            Ort_Churn_Olasiligi=("Churn_Proba", "mean"),
        ).reset_index()

        if "Gercek_Churn" in df_result.columns:
            gercek = df_result.groupby(group_col)["Gercek_Churn"].mean().reset_index()
            gercek.columns = [group_col, "Gercek_Churn_Orani"]
            group_stats = group_stats.merge(gercek, on=group_col)

        logger.info(f"{group_col} bazlı churn oranları hesaplandı")
        return group_stats
    except Exception as e:
        logger.error(f"Grup churn oranı hesaplama hatası: {e}")
        return None


def compute_disparate_impact(group_stats: pd.DataFrame, group_col: str) -> dict:
    """
    Disparate Impact oranını hesaplar.
    En düşük churn oranına sahip grup referans alınır ve en yüksek oran ile karşılaştırılır.

    Args:
        group_stats (pd.DataFrame): Grup bazlı churn istatistikleri.
        group_col (str): Gruplama sütunu.

    Returns:
        dict: Disparate impact oranı ve detayları.
    """
    rates = group_stats.set_index(group_col)["Tahmin_Churn_Orani"]

    min_rate = rates.min()
    max_rate = rates.max()
    min_group = rates.idxmin()
    max_group = rates.idxmax()

    # Sıfıra bölme koruması
    if min_rate == 0:
        di_ratio = float("inf") if max_rate > 0 else 1.0
    else:
        di_ratio = max_rate / min_rate

    result = {
        "disparate_impact": round(di_ratio, 4),
        "hedef": DISPARATE_IMPACT_THRESHOLD,
        "hedef_karsilandi": di_ratio < DISPARATE_IMPACT_THRESHOLD,
        "en_yuksek_grup": max_group,
        "en_yuksek_oran": round(max_rate * 100, 2),
        "en_dusuk_grup": min_group,
        "en_dusuk_oran": round(min_rate * 100, 2),
    }
    logger.info(
        f"Disparate Impact ({group_col}): {di_ratio:.4f} "
        f"({'✅ Hedef karşılandı' if result['hedef_karsilandi'] else '❌ Hedef karşılanmadı'})"
    )
    return result


def create_churn_rate_comparison_fig(
    group_stats: pd.DataFrame, group_col: str, title_suffix: str = ""
) -> go.Figure:
    """
    Grup bazlı churn oranı karşılaştırma bar grafiği oluşturur.

    Args:
        group_stats (pd.DataFrame): Grup bazlı istatistikler.
        group_col (str): Gruplama sütunu.
        title_suffix (str): Başlık soneki.

    Returns:
        go.Figure: Bar chart figürü.
    """
    fig = go.Figure()

    # Tahmin edilen churn oranı
    fig.add_trace(go.Bar(
        x=group_stats[group_col],
        y=group_stats["Tahmin_Churn_Orani"] * 100,
        name="Tahmin Edilen Churn (%)",
        marker_color="#3498db",
        text=[f"%{v*100:.1f}" for v in group_stats["Tahmin_Churn_Orani"]],
        textposition="auto",
    ))

    # Gerçek churn oranı (varsa)
    if "Gercek_Churn_Orani" in group_stats.columns:
        fig.add_trace(go.Bar(
            x=group_stats[group_col],
            y=group_stats["Gercek_Churn_Orani"] * 100,
            name="Gerçek Churn (%)",
            marker_color="#e74c3c",
            text=[f"%{v*100:.1f}" for v in group_stats["Gercek_Churn_Orani"]],
            textposition="auto",
        ))

    fig.update_layout(
        title=f"{group_col} Bazlı Churn Oranı Karşılaştırması{title_suffix}",
        xaxis_title=group_col,
        yaxis_title="Churn Oranı (%)",
        barmode="group",
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def create_disparate_impact_gauge(di_result: dict, group_col: str) -> go.Figure:
    """
    Disparate Impact oranını gauge (gösterge) grafiği ile görselleştirir.

    Args:
        di_result (dict): compute_disparate_impact fonksiyonunun çıktısı.
        group_col (str): Gruplama sütunu.

    Returns:
        go.Figure: Gauge figürü.
    """
    di_val = min(di_result["disparate_impact"], 3.0)  # Görsel sınırlama

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=di_val,
        title={"text": f"Disparate Impact ({group_col})", "font": {"size": 18}},
        delta={"reference": DISPARATE_IMPACT_THRESHOLD, "decreasing": {"color": "#2ecc71"}, "increasing": {"color": "#e74c3c"}},
        gauge={
            "axis": {"range": [0, 3], "tickwidth": 1},
            "bar": {"color": "#2c3e50"},
            "steps": [
                {"range": [0, 1.0], "color": "#2ecc71"},
                {"range": [1.0, DISPARATE_IMPACT_THRESHOLD], "color": "#f1c40f"},
                {"range": [DISPARATE_IMPACT_THRESHOLD, 3.0], "color": "#e74c3c"},
            ],
            "threshold": {
                "line": {"color": "#e74c3c", "width": 3},
                "thickness": 0.8,
                "value": DISPARATE_IMPACT_THRESHOLD,
            },
        },
    ))
    fig.update_layout(height=350, margin=dict(l=30, r=30, t=60, b=10))
    return fig


def create_probability_distribution_fig(
    df: pd.DataFrame, model, scaler, features: list, group_col: str
) -> Optional[go.Figure]:
    """
    Grup bazlı churn olasılığı dağılımı (violin plot) oluşturur.

    Args:
        df (pd.DataFrame): Ham veri seti.
        model: Eğitilmiş model.
        scaler: Scaler objesi.
        features (list): Model özellikleri.
        group_col (str): Gruplama sütunu.

    Returns:
        Optional[go.Figure]: Violin plot figürü veya None.
    """
    if group_col not in df.columns:
        return None

    try:
        from core.utils import preprocess_data

        X = df.drop(columns=["RowNumber", "CustomerId", "Surname", "Exited"], errors="ignore")
        X_processed = preprocess_data(X, features, scaler)
        y_proba = model.predict_proba(X_processed)[:, 1]

        df_plot = pd.DataFrame({
            group_col: df[group_col].values,
            "Churn Olasılığı": y_proba,
        })

        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]
        fig = go.Figure()

        for idx, group in enumerate(sorted(df_plot[group_col].unique())):
            subset = df_plot[df_plot[group_col] == group]
            fig.add_trace(go.Violin(
                y=subset["Churn Olasılığı"],
                name=str(group),
                box_visible=True,
                meanline_visible=True,
                line_color=colors[idx % len(colors)],
            ))

        fig.update_layout(
            title=f"{group_col} Bazlı Churn Olasılığı Dağılımı",
            yaxis_title="Churn Olasılığı",
            height=450,
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=True,
        )
        return fig
    except Exception as e:
        logger.error(f"Olasılık dağılımı oluşturma hatası: {e}")
        return None


def create_bias_summary_table(di_results: list[dict]) -> go.Figure:
    """
    Tüm gruplar için bias özet tablosu oluşturur.

    Args:
        di_results (list[dict]): Her grup için disparate impact sonuçları.

    Returns:
        go.Figure: Plotly tablo figürü.
    """
    rows = []
    for r in di_results:
        rows.append([
            r.get("group_col", "—"),
            f"{r['disparate_impact']:.4f}",
            f"< {r['hedef']}",
            "✅ Adil" if r["hedef_karsilandi"] else "❌ Önyargılı",
            f"{r['en_yuksek_grup']} (%{r['en_yuksek_oran']})",
            f"{r['en_dusuk_grup']} (%{r['en_dusuk_oran']})",
        ])

    headers = ["Analiz Boyutu", "Disparate Impact", "Hedef", "Durum", "En Yüksek Risk", "En Düşük Risk"]
    cell_vals = list(zip(*rows)) if rows else [[] for _ in headers]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{h}</b>" for h in headers],
            fill_color="#2c3e50", font=dict(color="white", size=12),
            align="center",
        ),
        cells=dict(
            values=cell_vals,
            fill_color=[["#ecf0f1"] * len(rows)],
            font=dict(color="black", size=11), align="center", height=30,
        ),
    )])
    fig.update_layout(
        title="Adillik ve Önyargı Özet Raporu",
        height=50 + 40 * (len(rows) + 1),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig
