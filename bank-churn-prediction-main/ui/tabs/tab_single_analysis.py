from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from agents.churn_agent import run_agent
from core.utils import preprocess_data
from services.prediction import get_shap_explainer, make_prediction


def _collect_customer_form_data() -> dict[str, Any]:
    """Müşteri parametre formunu render edip girilen değerleri döndürür.

    Returns:
        dict[str, Any]: Model tahmini için kullanılacak müşteri özellikleri.
    """
    st.subheader("Müşteri Parametreleri")
    col_form1, col_form2, col_form3 = st.columns(3)

    with col_form1:
        credit_score = st.number_input("Kredi Notu", min_value=300, max_value=850, value=650)
        age = st.number_input("Yaş", min_value=18, max_value=100, value=40)
        tenure = st.number_input(
            "Müşterilik Süresi (Yıl)", min_value=0, max_value=20, value=5
        )

    with col_form2:
        balance = st.number_input(
            "Hesap Bakiyesi (€)", min_value=0.0, value=50000.0, step=1000.0
        )
        est_salary = st.number_input(
            "Tahmini Maaş (€)", min_value=0.0, value=60000.0, step=1000.0
        )
        num_products = st.selectbox("Kullanılan Ürün Sayısı", [1, 2, 3, 4], index=1)

    with col_form3:
        geography = st.selectbox("Ülke", ["France", "Germany", "Spain"])
        gender = st.selectbox("Cinsiyet", ["Male", "Female"])
        has_cr_card = st.selectbox(
            "Kredi Kartı Var mı?",
            [1, 0],
            format_func=lambda value: "Evet" if value == 1 else "Hayır",
        )
        is_active = st.selectbox(
            "Aktif Müşteri mi?",
            [1, 0],
            format_func=lambda value: "Evet" if value == 1 else "Hayır",
        )

    return {
        "CreditScore": credit_score,
        "Geography": geography,
        "Gender": gender,
        "Age": age,
        "Tenure": tenure,
        "Balance": balance,
        "NumOfProducts": num_products,
        "HasCrCard": has_cr_card,
        "IsActiveMember": is_active,
        "EstimatedSalary": est_salary,
    }


def _append_risk_history(customer_data: dict[str, Any], churn_probability: float) -> None:
    """Oturum içi risk geçmişine son analizi ekler.

    Args:
        customer_data: Analiz edilen müşteri verisi.
        churn_probability: Yüzde cinsinden churn olasılığı.
    """
    st.session_state.risk_history.append(
        {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "risk": churn_probability,
            "label": (
                f"Kredi:{customer_data['CreditScore']} "
                f"Yaş:{customer_data['Age']} "
                f"Bakiye:€{customer_data['Balance']:,.0f}"
            ),
        }
    )


def _run_single_prediction(
    customer_data: dict[str, Any],
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> None:
    """Tekil tahmini çalıştırır ve sonucu oturum durumuna yazar.

    Args:
        customer_data: Tahmin edilecek müşteri verisi.
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.
    """
    with st.spinner("Yapay Zeka Hesaplarken Lütfen Bekleyin..."):
        result = make_prediction(customer_data, local_model, local_scaler, expected_features)
        churn_probability = result["churn_ihtimali"] * 100

        st.session_state.current_customer = customer_data
        st.session_state.base_risk = churn_probability
        st.session_state.prediction_result = result
        st.session_state.analyze_clicked = True
        _append_risk_history(customer_data, churn_probability)


def _render_financial_impact(
    customer_data: dict[str, Any],
    churn_probability: float,
) -> None:
    """CLTV ve beklenen kayıp metriklerini render eder.

    Args:
        customer_data: Analiz edilen müşteri verisi.
        churn_probability: Yüzde cinsinden churn olasılığı.
    """
    customer_value = customer_data["Balance"] + (customer_data["EstimatedSalary"] * 0.20)
    expected_loss = customer_value * (churn_probability / 100)

    st.write("---")
    st.subheader("💰 Finansal Etki Analizi (CLTV)")
    fin_col1, fin_col2, fin_col3 = st.columns(3)
    fin_col1.metric(label="Müşterinin Bankaya Değeri", value=f"€{customer_value:,.2f}")
    fin_col2.metric(label="Ayrılma İhtimali", value=f"%{churn_probability:.1f}")
    fin_col3.metric(
        label="Beklenen Finansal Kayıp",
        value=f"€{expected_loss:,.2f}",
        delta="- Risk Tutarı",
        delta_color="inverse",
    )


def _normalize_shap_values(shap_values: Any) -> np.ndarray:
    """SHAP çıktısını tek boyutlu değer dizisine dönüştürür.

    Args:
        shap_values: SHAP explainer tarafından üretilen ham değerler.

    Returns:
        np.ndarray: Özellik bazlı SHAP değerleri.
    """
    if isinstance(shap_values, list):
        shap_array = shap_values[1][0]
    else:
        shap_array = shap_values[0, :, 1] if len(shap_values.shape) == 3 else shap_values[0]

    return np.array(shap_array).flatten()


def _create_shap_bar_figure(
    shap_values: np.ndarray,
    expected_features: list[str],
) -> go.Figure:
    """SHAP değerleri için yatay çubuk grafik üretir.

    Args:
        shap_values: Özellik bazlı SHAP değerleri.
        expected_features: Modelin beklediği özellik listesi.

    Returns:
        go.Figure: SHAP açıklama grafiği.
    """
    sort_inds = np.argsort(np.abs(shap_values))
    sorted_features = np.array(expected_features)[sort_inds]
    sorted_shap = shap_values[sort_inds]
    colors = ["salmon" if float(value) > 0 else "lightgreen" for value in sorted_shap]

    fig_shap = go.Figure(
        go.Bar(
            x=sorted_shap,
            y=sorted_features,
            orientation="h",
            marker_color=colors,
        )
    )
    fig_shap.update_layout(
        xaxis_title="<- Riski Düşürenler | Riski Artıranlar ->",
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
    )
    return fig_shap


def _render_shap_analysis(
    customer_data: dict[str, Any],
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> None:
    """Tekil tahmin için SHAP açıklama bölümünü render eder.

    Args:
        customer_data: Analiz edilen müşteri verisi.
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.
    """
    if local_model is None:
        return

    st.markdown("### 💡 Neden Analizi (SHAP)")
    try:
        df_input_shap = pd.DataFrame([customer_data])
        scaled_input_shap = preprocess_data(df_input_shap, expected_features, local_scaler)
        explainer = get_shap_explainer(local_model)
        shap_values = explainer.shap_values(scaled_input_shap, check_additivity=False)
        shap_vals = _normalize_shap_values(shap_values)
        fig_shap = _create_shap_bar_figure(shap_vals, expected_features)
        st.plotly_chart(fig_shap, use_container_width=True)
    except Exception:
        import traceback

        st.warning("Görsel açıklama modeli (SHAP) hesaplanırken bir hata oluştu.")
        st.error(f"Hata Detayı: {traceback.format_exc()}")


def _create_risk_gauge(churn_probability: float) -> go.Figure:
    """Churn olasılığı için gösterge grafiği üretir.

    Args:
        churn_probability: Yüzde cinsinden churn olasılığı.

    Returns:
        go.Figure: Risk göstergesi.
    """
    return go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=churn_probability,
            title={"text": "Ayrılma İhtimali (%)", "font": {"size": 24}},
            gauge={
                "axis": {"range": [None, 100]},
                "bar": {"color": "black"},
                "steps": [
                    {"range": [0, 40], "color": "lightgreen"},
                    {"range": [40, 70], "color": "gold"},
                    {"range": [70, 100], "color": "salmon"},
                ],
            },
        )
    )


def _render_model_output(
    customer_data: dict[str, Any],
    result: dict[str, Any],
    churn_probability: float,
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> None:
    """Model çıktısı, SHAP açıklaması ve risk göstergesini render eder.

    Args:
        customer_data: Analiz edilen müşteri verisi.
        result: Model tahmin sonucu.
        churn_probability: Yüzde cinsinden churn olasılığı.
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.
    """
    st.write("---")
    res_col1, res_col2 = st.columns([1, 1])

    with res_col1:
        st.subheader("📊 Model Çıktısı")
        st.metric(label="Risk Kategorisi", value=result["risk_seviyesi"])
        _render_shap_analysis(customer_data, local_model, local_scaler, expected_features)

    with res_col2:
        st.plotly_chart(_create_risk_gauge(churn_probability), use_container_width=True)


def _render_ai_campaign_messages(agent_result: dict[str, Any]) -> None:
    """LLM kampanya mesajlarını veya kural tabanlı mesajı gösterir.

    Args:
        agent_result: Ajan akışından dönen kampanya sonucu.
    """
    gemini_msg = agent_result.get("gemini_campaign")
    groq_msg = agent_result.get("groq_campaign")
    openai_msg = agent_result.get("openai_campaign")

    if gemini_msg or groq_msg or openai_msg:
        st.markdown("### 🤖 Yapay Zeka Kampanya Önerileri Karşılaştırması")
        ai_cols = st.columns(2)

        with ai_cols[0]:
            st.markdown("#### 🔵 Google Gemini")
            if gemini_msg:
                st.success(gemini_msg)
            else:
                st.warning("Gemini API aktif değil veya yanıt vermedi.")

        with ai_cols[1]:
            st.markdown("#### 🟠 Groq (Llama3)")
            if groq_msg:
                st.info(groq_msg)
            elif openai_msg:
                st.markdown("#### 🟢 OpenAI")
                st.info(openai_msg)
            else:
                st.warning("Groq/OpenAI API aktif değil veya yanıt vermedi.")
        return

    st.markdown(
        f"> 📧 **Kural Tabanlı Kampanya Mesajı:** "
        f"{agent_result.get('campaign_message', '')}"
    )


def _render_campaign_details(agent_result: dict[str, Any]) -> None:
    """Ajan kampanya sonucunun detaylarını render eder.

    Args:
        agent_result: Ajan akışından dönen kampanya sonucu.
    """
    with st.expander("📋 Kampanya Detayları (Ajan Çıktısı)", expanded=True):
        ag_c1, ag_c2, ag_c3 = st.columns(3)
        contact_channel = agent_result.get("contact_channel", "—")
        contact_parts = contact_channel.split()

        ag_c1.metric("🎯 Kampanya Türü", agent_result.get("campaign_type", "—"))
        ag_c2.metric(
            "💰 Tahmini Bütçe",
            f"€{agent_result.get('estimated_budget', 0):,.0f}",
        )
        ag_c3.metric(
            "📢 İletişim",
            contact_parts[1] if len(contact_parts) > 1 else "Bildirim",
        )

        st.info(f"**Önerilen Sistem Aksiyonu:** {agent_result.get('recommended_action')}")
        _render_ai_campaign_messages(agent_result)
        st.caption(f"Aciliyet: {agent_result.get('urgency', '—').upper()}")


def _render_retention_campaign(
    customer_data: dict[str, Any],
    result: dict[str, Any],
    churn_probability: float,
) -> None:
    """Yüksek riskli müşteri için kampanya üretme bölümünü render eder.

    Args:
        customer_data: Analiz edilen müşteri verisi.
        result: Model tahmin sonucu.
        churn_probability: Yüzde cinsinden churn olasılığı.
    """
    if churn_probability <= 50:
        return

    st.warning("⚠️ Müşterinin ayrılma riski yüksek. Acil aksiyon alınması önerilir.")
    if st.button("🤖 AI Kurtarma Kampanyası Üret", use_container_width=True):
        with st.spinner("AI Kampanya Önerisi Hazırlanıyor..."):
            agent_result = run_agent(
                customer_id="CUST-1",
                churn_probability=churn_probability / 100,
                risk_level=result["risk_seviyesi"],
                customer_data=customer_data,
            )
            st.success("✨ Kampanya Önerisi Hazır!")
            _render_campaign_details(agent_result)


def _render_prediction_result(
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> None:
    """Oturumda kayıtlı tekil tahmin sonucunu render eder.

    Args:
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.
    """
    customer_data = st.session_state.current_customer
    churn_probability = st.session_state.base_risk
    result = st.session_state.prediction_result

    _render_financial_impact(customer_data, churn_probability)
    _render_model_output(
        customer_data,
        result,
        churn_probability,
        local_model,
        local_scaler,
        expected_features,
    )
    _render_retention_campaign(customer_data, result, churn_probability)


def render_tab_single_analysis(
    local_model: Any = None,
    local_scaler: Any = None,
    expected_features: list[str] = None,
) -> None:
    """Tekil müşteri risk analizi sekmesini render eder.

    Args:
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.
    """
    customer_data = _collect_customer_form_data()

    if st.button("🔍 Risk Analizi Yap", use_container_width=True):
        _run_single_prediction(customer_data, local_model, local_scaler, expected_features)

    if st.session_state.get("analyze_clicked", False):
        _render_prediction_result(local_model, local_scaler, expected_features)
