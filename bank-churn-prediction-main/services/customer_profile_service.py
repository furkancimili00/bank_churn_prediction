"""
Müşteri 360° Profil Kartı servis modülü.
Tekil müşteri için zengin profil kartı, SHAP waterfall ve benzer müşteri analizi sağlar.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.neighbors import NearestNeighbors
from typing import Optional
from core.logging_config import get_logger

logger = get_logger(__name__)


def create_profile_card_fig(customer_data: dict, risk_pct: float, risk_level: str) -> go.Figure:
    """
    Müşteri bilgilerini görsel bir profil kartında sergiler.

    Args:
        customer_data (dict): Müşteri özellikleri sözlüğü.
        risk_pct (float): Churn risk yüzdesi.
        risk_level (str): Risk seviyesi metni.

    Returns:
        go.Figure: Plotly tablo figürü (profil kartı).
    """
    label_map = {
        "CreditScore": "Kredi Notu",
        "Geography": "Ülke",
        "Gender": "Cinsiyet",
        "Age": "Yaş",
        "Tenure": "Müşterilik Süresi (Yıl)",
        "Balance": "Hesap Bakiyesi (€)",
        "NumOfProducts": "Ürün Sayısı",
        "HasCrCard": "Kredi Kartı",
        "IsActiveMember": "Aktif Üye",
        "EstimatedSalary": "Tahmini Maaş (€)",
    }
    format_map = {
        "Balance": lambda v: f"€{v:,.2f}",
        "EstimatedSalary": lambda v: f"€{v:,.2f}",
        "HasCrCard": lambda v: "Evet ✅" if v == 1 else "Hayır ❌",
        "IsActiveMember": lambda v: "Aktif ✅" if v == 1 else "Pasif ❌",
    }

    labels = []
    values = []
    for key, val in customer_data.items():
        labels.append(label_map.get(key, key))
        formatter = format_map.get(key, str)
        values.append(formatter(val))

    # Risk bilgisini ekle
    labels.extend(["Churn Riski (%)", "Risk Seviyesi"])
    risk_color = "🔴" if risk_pct > 70 else "🟡" if risk_pct > 40 else "🟢"
    values.extend([f"{risk_color} %{risk_pct:.1f}", risk_level])

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b>Özellik</b>", "<b>Değer</b>"],
            fill_color="#2c3e50", font=dict(color="white", size=13),
            align="center",
        ),
        cells=dict(
            values=[labels, values],
            fill_color=[["#ecf0f1"] * len(labels), ["white"] * len(labels)],
            font=dict(color="black", size=12), align=["left", "center"], height=30,
        ),
    )])
    fig.update_layout(
        title="👤 Müşteri Profil Kartı",
        height=50 + 32 * len(labels),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def create_shap_waterfall(
    customer_data: dict, model, scaler, expected_features: list
) -> Optional[go.Figure]:
    """
    SHAP waterfall grafiği oluşturur — her özelliğin risk üzerindeki
    kümülatif etkisini adım adım gösterir.

    Args:
        customer_data (dict): Müşteri verileri.
        model: Eğitilmiş model.
        scaler: Scaler objesi.
        expected_features (list): Model özellikleri.

    Returns:
        Optional[go.Figure]: Waterfall figürü veya None.
    """
    try:
        import shap
        from core.utils import preprocess_data

        df_input = pd.DataFrame([customer_data])
        scaled_input = preprocess_data(df_input, expected_features, scaler)

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(scaled_input, check_additivity=False)

        if isinstance(shap_values, list):
            vals = shap_values[1][0]
        else:
            vals = shap_values[0, :, 1] if len(shap_values.shape) == 3 else shap_values[0]

        vals = np.array(vals).flatten()

        # Büyükten küçüğe sırala
        sort_idx = np.argsort(np.abs(vals))[::-1]
        sorted_features = np.array(expected_features)[sort_idx]
        sorted_vals = vals[sort_idx]

        # Waterfall grafiği
        colors = ["#e74c3c" if v > 0 else "#2ecc71" for v in sorted_vals]

        fig = go.Figure(go.Waterfall(
            orientation="v",
            x=sorted_features.tolist(),
            y=sorted_vals.tolist(),
            connector={"line": {"color": "#7f8c8d", "width": 1}},
            increasing={"marker": {"color": "#e74c3c"}},
            decreasing={"marker": {"color": "#2ecc71"}},
            totals={"marker": {"color": "#3498db"}},
            textposition="outside",
            text=[f"{v:+.3f}" for v in sorted_vals],
        ))
        fig.update_layout(
            title="SHAP Waterfall — Özelliklerin Risk Üzerindeki Kümülatif Etkisi",
            yaxis_title="SHAP Değeri (Riske Katkı)",
            height=450,
            margin=dict(l=10, r=10, t=40, b=80),
        )
        logger.debug("SHAP waterfall grafiği oluşturuldu")
        return fig
    except Exception as e:
        logger.error(f"SHAP waterfall hatası: {e}")
        return None


def find_similar_customers(
    target_data: dict, dataset_path: str = "Churn_Modelling.csv", n_neighbors: int = 5
) -> Optional[pd.DataFrame]:
    """
    Hedef müşteriye en benzer müşterileri bulur (K-Nearest Neighbors).

    Args:
        target_data (dict): Hedef müşteri verileri.
        dataset_path (str): Veri seti dosya yolu.
        n_neighbors (int): Döndürülecek benzer müşteri sayısı.

    Returns:
        Optional[pd.DataFrame]: Benzer müşteriler DataFrame'i veya None.
    """
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        logger.warning(f"Veri seti bulunamadı: {dataset_path}")
        return None

    numeric_cols = ["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "EstimatedSalary"]
    available_cols = [c for c in numeric_cols if c in df.columns]

    if not available_cols:
        return None

    X = df[available_cols].values
    target_vals = np.array([[target_data.get(c, 0) for c in available_cols]])

    # Normalize
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    target_scaled = scaler.transform(target_vals)

    nn = NearestNeighbors(n_neighbors=min(n_neighbors, len(df)), metric="euclidean")
    nn.fit(X_scaled)
    distances, indices = nn.kneighbors(target_scaled)

    similar = df.iloc[indices[0]].copy()
    similar["Benzerlik Mesafesi"] = np.round(distances[0], 3)

    # Gösterilecek sütunlar
    display_cols = ["CustomerId", "CreditScore", "Age", "Geography", "Gender",
                    "Balance", "NumOfProducts", "Benzerlik Mesafesi"]
    if "Exited" in similar.columns:
        display_cols.append("Exited")

    display_cols = [c for c in display_cols if c in similar.columns]
    result = similar[display_cols].reset_index(drop=True)

    logger.debug(f"{n_neighbors} benzer müşteri bulundu")
    return result


def create_risk_history_chart(history: list[dict]) -> Optional[go.Figure]:
    """
    Oturum boyunca yapılan analizlerin risk zaman çizelgesini gösterir.

    Args:
        history (list[dict]): Her biri {'timestamp', 'risk', 'label'} içeren analiz geçmişi.

    Returns:
        Optional[go.Figure]: Çizgi grafik veya None.
    """
    if not history or len(history) < 1:
        return None

    timestamps = [h["timestamp"] for h in history]
    risks = [h["risk"] for h in history]
    labels = [h.get("label", "") for h in history]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(risks) + 1)),
        y=risks,
        mode="lines+markers+text",
        text=[f"%{r:.1f}" for r in risks],
        textposition="top center",
        marker=dict(
            size=12,
            color=["#e74c3c" if r > 70 else "#f39c12" if r > 40 else "#2ecc71" for r in risks],
        ),
        line=dict(color="#3498db", width=2),
        hovertext=labels,
    ))

    fig.add_hline(y=50, line_dash="dot", line_color="#e74c3c",
                  annotation_text="Risk Eşiği (%50)")

    fig.update_layout(
        title="📈 Oturum İçi Risk Analizi Geçmişi",
        xaxis_title="Analiz Sırası",
        yaxis_title="Churn Riski (%)",
        yaxis=dict(range=[0, 100]),
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def compute_customer_value_breakdown(customer_data: dict) -> go.Figure:
    """
    Müşterinin bankaya olan değerinin bileşenlerini gösteren grafik.

    Args:
        customer_data (dict): Müşteri verileri.

    Returns:
        go.Figure: Pie chart figürü.
    """
    balance = customer_data.get("Balance", 0)
    salary_contrib = customer_data.get("EstimatedSalary", 0) * 0.20
    products = customer_data.get("NumOfProducts", 1) * 500  # Her ürün ~€500 değer

    labels = ["Hesap Bakiyesi", "Maaş Katkısı (%20)", "Ürün Değeri"]
    values = [balance, salary_contrib, products]
    colors = ["#3498db", "#2ecc71", "#f39c12"]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo="label+percent",
        textposition="outside",
    )])
    fig.update_layout(
        title="💰 Müşteri Değeri Bileşenleri (CLTV)",
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
        annotations=[dict(text=f"€{sum(values):,.0f}", x=0.5, y=0.5, font_size=16, showarrow=False)],
    )
    return fig
