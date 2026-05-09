import os
os.environ["USE_TF"] = "NO"
os.environ["USE_TORCH"] = "NO"

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from core.utils import preprocess_data
from agents.churn_agent import run_agent, generate_management_report
from services.prediction import (
    load_local_model,
    get_shap_explainer,
    make_prediction,
    make_batch_prediction,
)
from services.eda_service import (
    load_default_dataset,
    create_correlation_heatmap,
    create_distribution_histograms,
    create_churn_boxplots,
    create_categorical_analysis,
    create_churn_rate_by_category,
    get_summary_statistics,
)
from services.model_metrics_service import (
    compute_all_metrics,
    create_confusion_matrix_fig,
    create_roc_curve_fig,
    create_precision_recall_fig,
    create_feature_importance_fig,
    create_metrics_comparison_table,
)
from services.segmentation_service import (
    find_optimal_k,
    perform_segmentation,
    create_pca_scatter,
    create_segment_profile,
    create_segment_summary_table,
    create_segment_churn_bar,
)
from services.fairness_service import (
    compute_group_churn_rates,
    compute_disparate_impact,
    create_churn_rate_comparison_fig,
    create_disparate_impact_gauge,
    create_probability_distribution_fig,
    create_bias_summary_table,
)
from services.customer_profile_service import (
    create_profile_card_fig,
    create_shap_waterfall,
    find_similar_customers,
    create_risk_history_chart,
    compute_customer_value_breakdown,
)
from services.data_privacy import (
    anonymize_dataframe,
    generate_privacy_report,
    detect_pii_columns,
)
from services.drift_service import (
    analyze_drift,
    create_drift_summary_table,
    create_drift_distribution_fig,
)
from services.audit_service import (
    log_event,
    get_recent_events,
    get_event_summary,
    clear_audit_log,
)

# Sayfa ayarları her zaman en üstte olmalıdır
st.set_page_config(page_title="Banka Churn Risk Paneli", page_icon="🏦", layout="wide")

# ==========================================
# 1. OTURUM (SESSION) YÖNETİMİ
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_customer" not in st.session_state:
    st.session_state.current_customer = None
if "base_risk" not in st.session_state:
    st.session_state.base_risk = None
if "risk_history" not in st.session_state:
    st.session_state.risk_history = []


# ==========================================
# 2. MODEL YÜKLEME (CACHE)
# ==========================================
local_model, local_scaler, expected_features = load_local_model()


# ==========================================
# 3. GİRİŞ (LOGIN) EKRANI FONKSİYONU
# ==========================================
def login_screen():
    """
    Kullanıcı girişi için kimlik doğrulama ekranını oluşturur.
    Giriş başarılı olduğunda oturum durumunu (session_state) günceller.
    """
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🏦</h1>", unsafe_allow_html=True)
        st.markdown(
            "<h3 style='text-align: center;'>Kurumsal Yönetici Girişi</h3>",
            unsafe_allow_html=True,
        )
        st.write("---")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if (
                username == st.secrets["auth"]["username"]
                and password == st.secrets["auth"]["password"]
            ):
                st.session_state.logged_in = True
                st.success("Giriş Başarılı!")
                st.rerun()
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre!")


# ==========================================
# 4. ANA PANEL (DASHBOARD) FONKSİYONU
# ==========================================
def main_dashboard():
    """
    Giriş başarılı olduktan sonra gösterilecek ana kontrol panelini (dashboard) oluşturur.
    Sekmeler halinde tekil analiz, simülasyon, toplu analiz ve yönetim raporlarını içerir.
    """
    st.sidebar.title("Yönetici Menüsü")
    st.sidebar.info("Hoş Geldiniz, **Şube Müdürü**")

    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Uygulama Hakkında")
    st.sidebar.write(
        "Bu panel, müşteri terk (churn) riskini analiz etmek, simüle etmek ve toplu değerlendirmeler yapmak için geliştirilmiştir."
    )
    st.sidebar.write(
        "Yapay Zeka (AI) destekli tahmin ve kampanya öneri sistemleri içerir."
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Genel Metrikler")
    st.sidebar.metric(label="Sistem Durumu", value="Aktif", delta="Model Yüklü")

    if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
        log_event("logout", {"user": "admin"})
        st.session_state.logged_in = False
        st.rerun()

    # Akademik Vitrin
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎓 Proje Hakkında")
    st.sidebar.markdown("""
    **Banka Müşteri Churn Tahmin Platformu**
    
    🎯 **Hedef Metrikler:**
    - F1 Score > 0.85
    - ROC-AUC > 0.90
    - API Yanıt < 1s
    
    ⚙️ **Teknoloji Yığını:**
    - XGBoost + SHAP
    - FastAPI + Streamlit
    - LangGraph + Loguru
    - Docker + CI/CD
    
    🌍 **SDG Uyumluluk:**
    - SDG 8: İnsana Yakışır İş
    - SDG 10: Eşitsizliklerin Azaltılması
    
    *v2.0.0 — Kurumsal Karar Destek Platformu*
    """)

    st.title("🏦 Şube Müdürü Müşteri Risk Analiz Paneli")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs(
        [
            "👤 Tekil Analiz",
            "🧪 What-If",
            "📂 Toplu Analiz",
            "📝 Yönetim Raporu",
            "📈 EDA",
            "🏆 Performans",
            "🎯 Segmentasyon",
            "⚖️ Adillik",
            "👤 Profil Kartı",
            "🔒 Gizlilik",
            "📉 Drift Analizi",
            "📜 Denetim Günlüğü",
        ]
    )


    # --- SEKM 1: TEKİL MÜŞTERİ ANALİZİ ---
    with tab1:
        st.subheader("Müşteri Parametreleri")
        col_form1, col_form2, col_form3 = st.columns(3)
        with col_form1:
            credit_score = st.number_input(
                "Kredi Notu", min_value=300, max_value=850, value=650
            )
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
                format_func=lambda x: "Evet" if x == 1 else "Hayır",
            )
            is_active = st.selectbox(
                "Aktif Müşteri mi?",
                [1, 0],
                format_func=lambda x: "Evet" if x == 1 else "Hayır",
            )

        if st.button("🔍 Risk Analizi Yap", use_container_width=True):
            customer_data = {
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

            with st.spinner("Yapay Zeka Hesaplarken Lütfen Bekleyin..."):
                # ARTIK API İSTEĞİ ATMIYORUZ, TAHMİNİ BURADA YAPIYORUZ
                result = make_prediction(
                    customer_data, local_model, local_scaler, expected_features
                )
                churn_probability = result["churn_ihtimali"] * 100
                st.session_state.current_customer = customer_data
                st.session_state.base_risk = churn_probability

                # Risk geçmişine ekle
                from datetime import datetime
                st.session_state.risk_history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "risk": churn_probability,
                    "label": f"Kredi:{credit_score} Yaş:{age} Bakiye:€{balance:,.0f}",
                })

                customer_value = balance + (est_salary * 0.20)
                expected_loss = customer_value * (churn_probability / 100)

                st.write("---")
                st.subheader("💰 Finansal Etki Analizi (CLTV)")
                fin_col1, fin_col2, fin_col3 = st.columns(3)
                fin_col1.metric(
                    label="Müşterinin Bankaya Değeri", value=f"€{customer_value:,.2f}"
                )
                fin_col2.metric(
                    label="Ayrılma İhtimali", value=f"%{churn_probability:.1f}"
                )
                fin_col3.metric(
                    label="Beklenen Finansal Kayıp",
                    value=f"€{expected_loss:,.2f}",
                    delta="- Risk Tutarı",
                    delta_color="inverse",
                )

                st.write("---")
                res_col1, res_col2 = st.columns([1, 1])
                with res_col1:
                    st.subheader("📊 Model Çıktısı")
                    st.metric(label="Risk Kategorisi", value=result["risk_seviyesi"])

                    # SHAP ANALİZİ (Önceden yaptığımız düzeltmelerle)
                    if local_model is not None:
                        st.markdown("### 💡 Neden Analizi (SHAP)")
                        try:
                            df_input_shap = pd.DataFrame([customer_data])

                            # Utils ile Ön İşleme
                            scaled_input_shap = preprocess_data(
                                df_input_shap, expected_features, local_scaler
                            )

                            explainer = get_shap_explainer(local_model)
                            shap_values = explainer.shap_values(
                                scaled_input_shap, check_additivity=False
                            )

                            if isinstance(shap_values, list):
                                shap_vals = shap_values[1][0]
                            else:
                                shap_vals = (
                                    shap_values[0, :, 1]
                                    if len(shap_values.shape) == 3
                                    else shap_values[0]
                                )

                            shap_vals = np.array(shap_vals).flatten()
                            sort_inds = np.argsort(np.abs(shap_vals))
                            sorted_features = np.array(expected_features)[sort_inds]
                            sorted_shap = shap_vals[sort_inds]
                            colors = [
                                "salmon" if float(val) > 0 else "lightgreen"
                                for val in sorted_shap
                            ]

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
                            st.plotly_chart(fig_shap, use_container_width=True)
                        except Exception as e:
                            import traceback
                            st.warning("Görsel açıklama modeli (SHAP) hesaplanırken bir hata oluştu.")
                            st.error(f"Hata Detayı: {traceback.format_exc()}")

                with res_col2:
                    fig_gauge = go.Figure(
                        go.Indicator(
                            mode="gauge+number",
                            value=churn_probability,
                            title={
                                "text": "Ayrılma İhtimali (%)",
                                "font": {"size": 24},
                            },
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
                    st.plotly_chart(fig_gauge, use_container_width=True)

                if churn_probability > 50:
                    st.warning(
                        "⚠️ Müşterinin ayrılma riski yüksek. Acil aksiyon alınması önerilir."
                    )
                    if st.button(
                        "🤖 AI Kurtarma Kampanyası Üret", use_container_width=True
                    ):
                        with st.spinner("AI Kampanya Önerisi Hazırlanıyor..."):
                            agent_result = run_agent(
                                customer_id="CUST-1",
                                churn_probability=churn_probability / 100,
                                risk_level=result["risk_seviyesi"],
                            )
                            st.success("✨ Kampanya Önerisi Hazır!")
                            with st.expander("📋 Kampanya Detayları (4 Adımlı Ajan Çıktısı)", expanded=True):
                                ag_c1, ag_c2 = st.columns(2)
                                ag_c1.metric("🎯 Kampanya Türü", agent_result.get('campaign_type', '—'))
                                ag_c2.metric("💰 Tahmini Bütçe", f"€{agent_result.get('estimated_budget', 0):,.0f}")
                                st.info(f"**Önerilen Aksiyon:** {agent_result.get('recommended_action')}")
                                st.success(f"📢 **İletişim Kanalı:** {agent_result.get('contact_channel', '—')}")
                                st.markdown(f"> 📧 **Kampanya Mesajı:** {agent_result.get('campaign_message', '')}")
                                st.caption(f"Aciliyet: {agent_result.get('urgency', '—').upper()}")

    # --- SEKM 2: WHAT-IF SİMÜLATÖRÜ ---
    with tab2:
        st.subheader("🧪 Müşteri Parametreleri Değişim Simülatörü")
        if st.session_state.current_customer is not None:
            cust = st.session_state.current_customer
            base_risk = st.session_state.base_risk

            st.info(
                "Aşağıdaki kaydırıcılar ve seçeneklerle müşteri özelliklerini değiştirerek ayrılma ihtimaline olan etkisini anlık olarak gözlemleyebilirsiniz."
            )

            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                st.markdown("#### Finansal Durum")
                new_balance = st.slider(
                    "Yeni Hesap Bakiyesi (€)",
                    min_value=0.0,
                    max_value=250000.0,
                    value=float(cust["Balance"]),
                    step=1000.0,
                    key="sim_bal",
                )
                new_est_salary = st.slider(
                    "Yeni Tahmini Maaş (€)",
                    min_value=0.0,
                    max_value=200000.0,
                    value=float(cust["EstimatedSalary"]),
                    step=1000.0,
                    key="sim_sal",
                )
            with sim_col2:
                st.markdown("#### Banka Ürün Kullanımı & Aktivite")
                new_products = st.slider(
                    "Ürün Sayısını Değiştir",
                    1,
                    4,
                    value=int(cust["NumOfProducts"]),
                    key="sim_prod",
                )
                new_active = st.selectbox(
                    "Müşteriyi Aktif Hale Getir?",
                    [1, 0],
                    index=0 if cust["IsActiveMember"] == 1 else 1,
                    key="sim_act",
                )
                new_crcard = st.selectbox(
                    "Kredi Kartı Kampanyası Tanımla?",
                    [1, 0],
                    index=0 if cust["HasCrCard"] == 1 else 1,
                    key="sim_cr",
                )

            if st.button(
                "🔄 Değişim Senaryosunu Simüle Et",
                type="primary",
                use_container_width=True,
            ):
                sim_data = cust.copy()
                sim_data.update(
                    {
                        "Balance": new_balance,
                        "EstimatedSalary": new_est_salary,
                        "IsActiveMember": new_active,
                        "HasCrCard": new_crcard,
                        "NumOfProducts": new_products,
                    }
                )

                # SİMÜLASYONDA DA YEREL TAHMİN KULLANILIYOR
                with st.spinner("Simülasyon hesaplanıyor..."):
                    res_sim = make_prediction(
                        sim_data, local_model, local_scaler, expected_features
                    )
                    new_risk = res_sim["churn_ihtimali"] * 100
                    diff = new_risk - base_risk

                st.write("---")
                st.subheader("📈 Simülasyon Sonuçları")

                res_sim_col1, res_sim_col2 = st.columns(2)

                with res_sim_col1:
                    st.metric(label="Mevcut Ayrılma Riski", value=f"%{base_risk:.1f}")
                    if diff < 0:
                        st.metric(
                            label="Simüle Edilen Yeni Risk",
                            value=f"%{new_risk:.1f}",
                            delta=f"{diff:.1f} Puan (İyileşme)",
                            delta_color="normal",
                        )
                    else:
                        st.metric(
                            label="Simüle Edilen Yeni Risk",
                            value=f"%{new_risk:.1f}",
                            delta=f"+{diff:.1f} Puan (Kötüleşme)",
                            delta_color="inverse",
                        )

                with res_sim_col2:
                    # Basit bir çubuk grafik ile karşılaştırma
                    fig_comp = go.Figure()
                    fig_comp.add_trace(
                        go.Bar(
                            x=["Mevcut Durum", "Simülasyon"],
                            y=[base_risk, new_risk],
                            marker_color=[
                                "salmon",
                                "lightgreen" if diff < 0 else "red",
                            ],
                            text=[f"%{base_risk:.1f}", f"%{new_risk:.1f}"],
                            textposition="auto",
                        )
                    )
                    fig_comp.update_layout(
                        title="Risk Karşılaştırması",
                        yaxis_title="Ayrılma İhtimali (%)",
                        yaxis=dict(range=[0, 100]),
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)

        else:
            st.warning(
                "Lütfen önce 'Tekil Müşteri Analizi' sekmesinden bir analiz yapın."
            )

    # --- SEKM 3: TOPLU MÜŞTERİ YÜKLEME ---
    with tab3:
        st.subheader("📁 Toplu Müşteri Analizi ve Önceliklendirme")
        st.write(
            "Müşteri verilerinizi içeren CSV dosyasını yükleyerek toplu risk analizi yapabilir ve beklenen finansal kayba göre önceliklendirme alabilirsiniz."
        )

        uploaded_file = st.file_uploader("CSV Dosyası Seçin", type=["csv"])

        if uploaded_file is not None:
            MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error(
                    "❌ Yüklenen dosya boyutu çok büyük! Maksimum 5MB yükleyebilirsiniz."
                )
            else:
                try:
                    df = pd.read_csv(uploaded_file)

                    required_columns = {
                        "CreditScore": "int64",
                        "Geography": "object",
                        "Gender": "object",
                        "Age": "int64",
                        "Tenure": "int64",
                        "Balance": "float64",
                        "NumOfProducts": "int64",
                        "HasCrCard": "int64",
                        "IsActiveMember": "int64",
                        "EstimatedSalary": "float64",
                    }
                    missing_columns = [
                        col for col in required_columns.keys() if col not in df.columns
                    ]

                    if missing_columns:
                        st.error(
                            f"❌ Yüklenen dosyada eksik sütunlar var: {', '.join(missing_columns)}"
                        )
                    elif df.empty:
                        st.error("❌ Yüklenen dosya boş.")
                    elif len(df) > 10000:
                        st.error(
                            "❌ Dosya çok fazla satır içeriyor. Lütfen en fazla 10.000 satırlık bir dosya yükleyin."
                        )
                    else:
                        st.success(
                            f"✅ Dosya başarıyla yüklendi. Toplam {len(df)} müşteri kaydı bulundu."
                        )

                        # Tip zorlama ve doğrulama (Schema validation)
                        try:
                            # Sayısal olması gerekenleri sayısal tipe zorluyoruz
                            numeric_cols = [
                                "CreditScore",
                                "Age",
                                "Tenure",
                                "Balance",
                                "NumOfProducts",
                                "HasCrCard",
                                "IsActiveMember",
                                "EstimatedSalary",
                            ]
                            for col in numeric_cols:
                                df[col] = pd.to_numeric(df[col], errors="raise")

                            # Tür dönüşümü başarılı oldu, analiz adımına geçebiliriz
                            schema_valid = True
                        except ValueError as e:
                            st.error(
                                f"❌ Veri tipi hatası: Dosyadaki veriler beklenilen sayısal formatta değil. Detay: {e}"
                            )
                            schema_valid = False

                        if schema_valid and st.button(
                            "🚀 Tüm Listeyi Analiz Et",
                            use_container_width=True,
                            type="primary",
                        ):
                            with st.spinner(
                                "Toplu analiz yapılıyor... Lütfen bekleyin."
                            ):
                                progress_bar = st.progress(0)

                                # Vektörel işlemlerle toplu tahmin ve hesaplamalar
                                df_input = df[list(required_columns.keys())].copy()

                                probs = make_batch_prediction(
                                    df_input,
                                    local_model,
                                    local_scaler,
                                    expected_features,
                                )
                                progress_bar.progress(0.5)

                                c_values = df["Balance"] + (
                                    df["EstimatedSalary"] * 0.20
                                )
                                exp_losses = c_values * probs

                                def get_risk_level(p):
                                    if p > 0.7:
                                        return "Yüksek"
                                    if p > 0.4:
                                        return "Orta"
                                    return "Düşük"

                                risk_levels = [get_risk_level(p) for p in probs]
                                customer_ids = (
                                    df["CustomerId"]
                                    if "CustomerId" in df.columns
                                    else df.index
                                )

                                results_df = pd.DataFrame(
                                    {
                                        "Müşteri ID": customer_ids,
                                        "Risk (%)": np.round(probs * 100, 2),
                                        "Risk Seviyesi": risk_levels,
                                        "Müşteri Değeri (€)": np.round(c_values, 2),
                                        "Beklenen Kayıp (€)": np.round(exp_losses, 2),
                                    }
                                )

                                progress_bar.progress(1.0)

                                results_df = results_df.sort_values(
                                    by="Beklenen Kayıp (€)", ascending=False
                                ).reset_index(drop=True)
                                
                                st.session_state.results_df = results_df

                                st.write("---")
                                st.subheader("📊 Analiz Özeti")

                                total_loss = results_df["Beklenen Kayıp (€)"].sum()
                                high_risk_count = len(
                                    results_df[results_df["Risk Seviyesi"] == "Yüksek"]
                                )

                                summary_col1, summary_col2 = st.columns(2)
                                summary_col1.metric(
                                    label="Toplam Beklenen Finansal Kayıp",
                                    value=f"€{total_loss:,.2f}",
                                )
                                summary_col2.metric(
                                    label="Yüksek Riskli Müşteri Sayısı",
                                    value=str(high_risk_count),
                                )

                                st.write("---")
                                st.subheader(
                                    "📋 Detaylı Müşteri Listesi (CLTV Öncelikli)"
                                )

                                def color_risk(val):
                                    return f"color: {'red' if 'Yüksek' in str(val) else 'orange' if 'Orta' in str(val) else 'green'}"

                                styled_df = results_df.style.map(
                                    color_risk, subset=["Risk Seviyesi"]
                                ).format(
                                    {
                                        "Müşteri Değeri (€)": "{:,.2f}",
                                        "Beklenen Kayıp (€)": "{:,.2f}",
                                    }
                                )

                                st.dataframe(styled_df, use_container_width=True)

                                csv = results_df.to_csv(index=False).encode("utf-8")
                                st.download_button(
                                    "📥 Analiz Raporunu İndir",
                                    data=csv,
                                    file_name="toplu_churn_analiz_raporu.csv",
                                    mime="text/csv",
                                )
                except Exception as e:
                    st.error(f"❌ Dosya okunurken bir hata oluştu: {e}")

    # --- SEKM 4: YÖNETİM RAPORU (RAG) ---
    with tab4:
        st.subheader("📝 Yönetim Raporu (RAG)")

        if "results_df" in st.session_state:
            st.info("Toplu analiz verileri hazır. Aşağıdaki butona basarak yönetim raporunu oluşturabilirsiniz.")

            if st.button("📊 Rapor Oluştur", use_container_width=True, type="primary"):
                with st.spinner("RAG Modülü: Rapor oluşturuluyor..."):
                    report_md = generate_management_report(st.session_state.results_df)
                    st.session_state.management_report = report_md

            if "management_report" in st.session_state:
                st.markdown(st.session_state.management_report)

                st.download_button(
                    label="📄 Raporu Markdown Olarak İndir",
                    data=st.session_state.management_report,
                    file_name="yonetim_raporu.md",
                    mime="text/markdown"
                )
        else:
            st.warning("⚠️ Lütfen önce 'Toplu Analiz' sekmesinden bir CSV dosyası yükleyerek analiz yapın. Rapor bu veriler üzerinden oluşturulacaktır.")

    # --- SEKME 5: KEŞİFSEL VERİ ANALİZİ (EDA) ---
    with tab5:
        st.subheader("📈 Keşifsel Veri Analizi (EDA)")
        st.write(
            "Veri setini interaktif grafiklerle keşfedin. Varsayılan olarak eğitim verisi kullanılır, "
            "veya kendi CSV dosyanızı yükleyebilirsiniz."
        )

        eda_source = st.radio(
            "Veri Kaynağı Seçin:",
            ["Varsayılan Veri Seti (Churn_Modelling.csv)", "Kendi CSV Dosyamı Yükle"],
            horizontal=True,
            key="eda_source",
        )

        eda_df = None
        if eda_source == "Varsayılan Veri Seti (Churn_Modelling.csv)":
            eda_df = load_default_dataset()
        else:
            eda_file = st.file_uploader("CSV Dosyası Yükle", type=["csv"], key="eda_upload")
            if eda_file is not None:
                eda_df = pd.read_csv(eda_file)

        if eda_df is not None:
            # Özet İstatistikler
            stats = get_summary_statistics(eda_df)
            st.markdown("### 📊 Genel Bakış")
            eda_m1, eda_m2, eda_m3, eda_m4 = st.columns(4)
            eda_m1.metric("Toplam Müşteri", f"{stats['toplam_musteri']:,}")
            eda_m2.metric("Ortalama Yaş", f"{stats['ortalama_yas']}" if stats['ortalama_yas'] else "—")
            eda_m3.metric("Ort. Bakiye (€)", f"€{stats['ortalama_bakiye']:,.0f}" if stats['ortalama_bakiye'] else "—")
            eda_m4.metric("Churn Oranı", f"%{stats['churn_orani']}" if stats['churn_orani'] is not None else "—")

            st.write("---")

            # Korelasyon Haritası
            st.markdown("### 🔗 Korelasyon Matrisi")
            fig_corr = create_correlation_heatmap(eda_df)
            st.plotly_chart(fig_corr, use_container_width=True)

            # Dağılım Histogramları
            st.markdown("### 📊 Özellik Dağılımları")
            fig_dist = create_distribution_histograms(eda_df)
            st.plotly_chart(fig_dist, use_container_width=True)

            # Box Plot'lar
            fig_box = create_churn_boxplots(eda_df)
            if fig_box is not None:
                st.markdown("### 📦 Churn Karşılaştırmalı Box Plot")
                st.plotly_chart(fig_box, use_container_width=True)

            # Kategorik Churn Oranları
            fig_cat_rate = create_churn_rate_by_category(eda_df)
            if fig_cat_rate is not None:
                st.markdown("### 📋 Kategorik Değişkenlere Göre Churn Oranı")
                st.plotly_chart(fig_cat_rate, use_container_width=True)

            # Çapraz Analiz (Sunburst)
            fig_sun = create_categorical_analysis(eda_df)
            if fig_sun is not None:
                st.markdown("### 🌐 Coğrafya → Cinsiyet → Churn (Sunburst)")
                st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("Lütfen bir veri kaynağı seçin veya CSV dosyası yükleyin.")

    # --- SEKME 6: MODEL PERFORMANSI ---
    with tab6:
        st.subheader("🏆 Model Performans İzleme")
        st.write(
            "Eğitilmiş XGBoost modelinin performans metriklerini, "
            "tez hedefleriyle karşılaştırmalı olarak inceleyin."
        )

        if local_model is not None:
            perf_df = load_default_dataset()
            if perf_df is not None:
                with st.spinner("Model metrikleri hesaplanıyor..."):
                    metrics = compute_all_metrics(
                        local_model, local_scaler, expected_features, perf_df
                    )

                if metrics is not None:
                    # Metrik Karşılaştırma Tablosu
                    st.markdown("### 📋 Tez Hedefleri Karşılaştırması")
                    fig_table = create_metrics_comparison_table(metrics)
                    st.plotly_chart(fig_table, use_container_width=True)

                    st.write("---")
                    perf_col1, perf_col2 = st.columns(2)

                    # Confusion Matrix
                    with perf_col1:
                        st.markdown("### 🔢 Karışıklık Matrisi")
                        fig_cm = create_confusion_matrix_fig(metrics["y_true"], metrics["y_pred"])
                        st.plotly_chart(fig_cm, use_container_width=True)

                    # Feature Importance
                    with perf_col2:
                        st.markdown("### 🎯 Özellik Önem Sıralaması")
                        fig_fi = create_feature_importance_fig(local_model, expected_features)
                        if fig_fi is not None:
                            st.plotly_chart(fig_fi, use_container_width=True)
                        else:
                            st.info("Bu model Feature Importance desteklemiyor.")

                    st.write("---")
                    roc_col, pr_col = st.columns(2)

                    # ROC Eğrisi
                    with roc_col:
                        st.markdown("### 📈 ROC Eğrisi")
                        fig_roc = create_roc_curve_fig(metrics["y_true"], metrics["y_proba"])
                        st.plotly_chart(fig_roc, use_container_width=True)

                    # Precision-Recall Eğrisi
                    with pr_col:
                        st.markdown("### 📉 Precision-Recall Eğrisi")
                        fig_pr = create_precision_recall_fig(metrics["y_true"], metrics["y_proba"])
                        st.plotly_chart(fig_pr, use_container_width=True)
                else:
                    st.error("Model metrikleri hesaplanamadı. Lütfen veri setini kontrol edin.")
            else:
                st.warning("⚠️ Varsayılan veri seti (Churn_Modelling.csv) bulunamadı.")
        else:
            st.error("❌ Model yüklenemedi. Model performansı gösterilemiyor.")

    # --- SEKME 7: MÜŞTERİ SEGMENTASYONU ---
    with tab7:
        st.subheader("🎯 Müşteri Segmentasyonu (K-Means Kümeleme)")
        st.write(
            "Müşterilerinizi davranış ve demografik özelliklerine göre otomatik segmentlere ayırın. "
            "Her segmentin risk profilini ve özelliklerini keşfedin."
        )

        seg_df = load_default_dataset()
        if seg_df is not None:
            # Elbow Method
            with st.expander("📀 Optimum Küme Sayısı Seçimi (Elbow Method)", expanded=False):
                fig_elbow = find_optimal_k(seg_df)
                st.plotly_chart(fig_elbow, use_container_width=True)
                st.caption("Grafiğin dirsek (elbow) noktası, optimum küme sayısını gösterir.")

            n_clusters = st.slider(
                "Küme Sayısını Seçin (k):", min_value=2, max_value=6, value=3, key="seg_k"
            )

            if st.button("🚀 Segmentasyonu Başlat", use_container_width=True, type="primary"):
                with st.spinner("Kümeleme analizi yapılıyor..."):
                    df_seg, X_scaled, _ = perform_segmentation(seg_df, n_clusters)

                    # Özet Tablosu
                    st.markdown("### 📋 Segment Özet Tablosu")
                    fig_summary = create_segment_summary_table(df_seg)
                    st.plotly_chart(fig_summary, use_container_width=True)

                    st.write("---")
                    seg_col1, seg_col2 = st.columns(2)

                    # PCA Scatter
                    with seg_col1:
                        st.markdown("### 📊 PCA Kümeleme Görselleştirmesi")
                        fig_pca = create_pca_scatter(df_seg, X_scaled)
                        st.plotly_chart(fig_pca, use_container_width=True)

                    # Segment Churn Oranları
                    with seg_col2:
                        fig_churn_bar = create_segment_churn_bar(df_seg)
                        if fig_churn_bar is not None:
                            st.markdown("### 📊 Segment Bazında Churn Oranı")
                            st.plotly_chart(fig_churn_bar, use_container_width=True)

                    st.write("---")
                    # Radar Profil
                    st.markdown("### 🕸️ Segment Profilleri (Radar)")
                    fig_radar = create_segment_profile(df_seg)
                    st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.warning("⚠️ Varsayılan veri seti bulunamadı.")

    # --- SEKME 8: ADİLLİK VE ÖNYARGI (FAIRNESS) ---
    with tab8:
        st.subheader("⚖️ Adillik ve Önyargı Analizi (Fairness/Bias)")
        st.write(
            "Modelin cinsiyet ve coğrafya bazında adil tahmin yapıp yapmadığını analiz edin. "
            "Tez hedefi: Disparate Impact < 1.2"
        )

        if local_model is not None:
            fair_df = load_default_dataset()
            if fair_df is not None:
                with st.spinner("Adillik analizi yapılıyor..."):
                    all_di_results = []

                    for group_col in ["Gender", "Geography"]:
                        group_stats = compute_group_churn_rates(
                            fair_df, local_model, local_scaler, expected_features, group_col
                        )
                        if group_stats is not None:
                            di_result = compute_disparate_impact(group_stats, group_col)
                            di_result["group_col"] = group_col
                            all_di_results.append(di_result)

                # Bias Özet Tablosu
                if all_di_results:
                    st.markdown("### 📋 Adillik Özet Raporu")
                    fig_bias_table = create_bias_summary_table(all_di_results)
                    st.plotly_chart(fig_bias_table, use_container_width=True)

                st.write("---")

                # Cinsiyet ve Coğrafya Analizi
                for group_col in ["Gender", "Geography"]:
                    st.markdown(f"### 🔍 {group_col} Bazında Analiz")

                    group_stats = compute_group_churn_rates(
                        fair_df, local_model, local_scaler, expected_features, group_col
                    )

                    if group_stats is not None:
                        di_result = compute_disparate_impact(group_stats, group_col)

                        fair_col1, fair_col2 = st.columns(2)

                        with fair_col1:
                            fig_bar = create_churn_rate_comparison_fig(group_stats, group_col)
                            st.plotly_chart(fig_bar, use_container_width=True)

                        with fair_col2:
                            fig_gauge = create_disparate_impact_gauge(di_result, group_col)
                            st.plotly_chart(fig_gauge, use_container_width=True)

                        # Violin Plot
                        fig_violin = create_probability_distribution_fig(
                            fair_df, local_model, local_scaler, expected_features, group_col
                        )
                        if fig_violin is not None:
                            st.plotly_chart(fig_violin, use_container_width=True)

                        st.write("---")
            else:
                st.warning("⚠️ Varsayılan veri seti bulunamadı.")
        else:
            st.error("❌ Model yüklenemedi.")

    # --- SEKME 9: MÜŞTERİ 360° PROFİL KARTI ---
    with tab9:
        st.subheader("👤 Müşteri 360° Profil Kartı")
        st.write(
            "Tekil Analiz sekmesinden analiz yapıldıktan sonra, müşterinin tüm bilgileri, "
            "risk detayları ve benzer müşteriler burada görüntülenir."
        )

        if st.session_state.current_customer is not None and st.session_state.base_risk is not None:
            cust = st.session_state.current_customer
            risk = st.session_state.base_risk
            risk_level = "Yüksek" if risk > 70 else "Orta" if risk > 40 else "Düşük"

            prof_col1, prof_col2 = st.columns([1, 1])

            with prof_col1:
                # Profil Kartı
                fig_card = create_profile_card_fig(cust, risk, risk_level)
                st.plotly_chart(fig_card, use_container_width=True)

            with prof_col2:
                # CLTV Bileşen Grafiği
                fig_cltv = compute_customer_value_breakdown(cust)
                st.plotly_chart(fig_cltv, use_container_width=True)

            st.write("---")

            # SHAP Waterfall
            if local_model is not None:
                st.markdown("### 🌊 SHAP Waterfall Analizi")
                fig_waterfall = create_shap_waterfall(cust, local_model, local_scaler, expected_features)
                if fig_waterfall is not None:
                    st.plotly_chart(fig_waterfall, use_container_width=True)
                else:
                    st.info("SHAP Waterfall hesaplanamadı.")

            st.write("---")

            # Risk Geçmişi
            if st.session_state.risk_history:
                st.markdown("### 📈 Oturum İçi Risk Analizi Geçmişi")
                fig_history = create_risk_history_chart(st.session_state.risk_history)
                if fig_history is not None:
                    st.plotly_chart(fig_history, use_container_width=True)

            st.write("---")

            # Benzer Müşteriler
            st.markdown("### 🔍 Benzer Profilli Müşteriler")
            n_similar = st.slider("Gösterilecek benzer müşteri sayısı:", 3, 10, 5, key="sim_n")
            similar_df = find_similar_customers(cust, n_neighbors=n_similar)
            if similar_df is not None:
                st.dataframe(similar_df, use_container_width=True)
            else:
                st.info("Veri seti bulunamadığı için benzer müşteriler gösterilemiyor.")
        else:
            st.warning(
                "⚠️ Lütfen önce '👤 Tekil Analiz' sekmesinden bir müşteri analizi yapın."
            )

    # --- SEKME 10: VERİ GİZLİLİĞİ (KVKK/GDPR) ---
    with tab10:
        st.subheader("🔒 Veri Gizliliği ve Anonimleştirme (KVKK/GDPR)")
        st.write(
            "CSV dosyanızdaki kişisel verileri (ad, soyad, müşteri ID) otomatik tespit edip "
            "maskeleyerek KVKK/GDPR uyumlu hale getirin."
        )

        privacy_file = st.file_uploader(
            "Anonimleştirilecek CSV Dosyası Yükleyin", type=["csv"], key="privacy_upload"
        )

        if privacy_file is not None:
            df_original = pd.read_csv(privacy_file)
            st.success(f"✅ {len(df_original)} satırlık dosya yüklendi.")

            # PII Tespiti
            pii_cols = detect_pii_columns(df_original)
            if pii_cols:
                st.info(f"🔍 Tespit edilen kişisel veri sütunları: **{', '.join(pii_cols)}**")
            else:
                st.warning("⚠️ Otomatik PII tespiti yapılamadı. Manuel sütun seçebilirsiniz.")

            # Maskeleme yöntemi seçimi
            mask_method = st.selectbox(
                "Maskeleme Yöntemi Seçin:",
                ["hash", "partial", "redact"],
                format_func=lambda x: {
                    "hash": "🔐 SHA-256 Hash (Geri Döndürülemez)",
                    "partial": "🔤 Kısmi Maskeleme (İlk/Son Harf Görünür)",
                    "redact": "🚫 Tam Gizleme ([GİZLİ] ile değiştirilir)",
                }[x],
                key="mask_method",
            )

            if st.button("🛡️ Anonimleştir ve İndir", use_container_width=True, type="primary"):
                with st.spinner("Veriler anonimleştiriliyor..."):
                    df_anon = anonymize_dataframe(df_original, method=mask_method)
                    privacy_report = generate_privacy_report(df_original, df_anon)

                # Gizlilik Raporu
                st.markdown("### 📋 Gizlilik Raporu")
                priv_c1, priv_c2, priv_c3 = st.columns(3)
                priv_c1.metric("Toplam Satır", f"{privacy_report['toplam_satir']:,}")
                priv_c2.metric("Maskelenen Sütun", str(privacy_report['maskelenen_sutun_sayisi']))
                priv_c3.metric("KVKK Durumu", privacy_report['kvkk_uyumluluk'])

                # Önizleme
                st.markdown("### 👁️ Anonimleştirilmiş Veri Önizlemesi (İlk 10 Satır)")
                st.dataframe(df_anon.head(10), use_container_width=True)

                # İndirme
                csv_anon = df_anon.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Anonimleştirilmiş Veriyi İndir",
                    data=csv_anon,
                    file_name="anonim_veri.csv",
                    mime="text/csv",
                )

    # --- SEKME 11: DRİFT ANALİZİ ---
    with tab11:
        st.subheader("📉 Veri Drift Analizi")
        st.write(
            "Yeni yüklediğiniz veriyi eğitim verisine kıyaslayın. "
            "PSI ve KS testleri ile dağılım kaymalarını tespit edin."
        )

        drift_file = st.file_uploader(
            "Karşılaştırılacak CSV Dosyası Yükleyin", type=["csv"], key="drift_upload"
        )

        ref_df = load_default_dataset()
        if drift_file is not None and ref_df is not None:
            cur_df = pd.read_csv(drift_file)
            st.success(f"✅ {len(cur_df)} satırlık dosya yüklendi. Referans: {len(ref_df)} satır.")

            with st.spinner("Drift analizi yapılıyor..."):
                drift_results = analyze_drift(ref_df, cur_df)

            if drift_results:
                # Özet bilgi kartları
                drifted = sum(1 for r in drift_results if "Kritik" in r["severity"] or "Uyarı" in r["severity"])
                dr_c1, dr_c2, dr_c3 = st.columns(3)
                dr_c1.metric("İncelenen Özellik", len(drift_results))
                dr_c2.metric("Drift Tespit Edilen", drifted)
                dr_c3.metric("Durum", "⚠️ Drift Var" if drifted > 0 else "✅ Normal")

                # Drift Tablosu
                fig_drift = create_drift_summary_table(drift_results)
                st.plotly_chart(fig_drift, use_container_width=True)

                # Dağılım Karşılaştırmaları
                st.markdown("### 📊 Dağılım Karşılaştırmaları")
                drifted_features = [r["feature"] for r in drift_results if r["psi"] > 0.05]
                if not drifted_features:
                    drifted_features = [drift_results[0]["feature"]] if drift_results else []

                for feat in drifted_features[:4]:
                    fig_dist = create_drift_distribution_fig(ref_df, cur_df, feat)
                    st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info("Ortak sayısal sütun bulunamadı.")
        elif drift_file is None:
            st.info("📄 Lütfen karşılaştırmak için bir CSV dosyası yükleyin.")
        else:
            st.warning("⚠️ Referans veri seti (Churn_Modelling.csv) bulunamadı.")

    # --- SEKME 12: DENETİM GÜNLÜĞÜ ---
    with tab12:
        st.subheader("📜 Denetim Günlüğü (Audit Log)")
        st.write("Sistemde gerçekleşen tüm işlemlerin zaman damgalı kayıtları.")

        summary = get_event_summary()

        aud_c1, aud_c2, aud_c3 = st.columns(3)
        aud_c1.metric("Toplam Kayıt", summary.get("toplam_kayit", 0))
        aud_c2.metric("Son Olay", summary.get("son_olay", "—")[:19] if summary.get("son_olay") else "—")
        event_types = summary.get("olay_tipleri", {})
        aud_c3.metric("Olay Türü Sayısı", len(event_types))

        if event_types:
            st.markdown("### 📊 Olay Türü Dağılımı")
            import plotly.express as px
            df_events = pd.DataFrame([
                {"Olay Türü": k, "Sayı": v} for k, v in event_types.items()
            ])
            fig_ev = px.bar(df_events, x="Olay Türü", y="Sayı", color="Olay Türü")
            fig_ev.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_ev, use_container_width=True)

        st.markdown("### 📝 Son Kayıtlar")
        n_events = st.slider("Gösterilecek kayıt sayısı:", 5, 100, 20, key="audit_n")
        events = get_recent_events(limit=n_events)
        if events:
            df_log = pd.DataFrame(events)
            st.dataframe(df_log, use_container_width=True)
        else:
            st.info("Henüz denetim kaydı bulunmuyor.")

        if st.button("🗑️ Denetim Logunu Temizle", type="secondary"):
            clear_audit_log()
            st.success("Denetim logu temizlendi.")
            st.rerun()

# --- AKIŞ KONTROLÜ ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_dashboard()
