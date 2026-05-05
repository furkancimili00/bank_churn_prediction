import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import skops.io as sio
import shap
import numpy as np
from utils import preprocess_data

# Sayfa ayarları her zaman en üstte olmalıdır
st.set_page_config(page_title="Banka Churn Risk Paneli", page_icon="🏦", layout="wide")

# ==========================================
# 1. OTURUM (SESSION) YÖNETİMİ
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_customer' not in st.session_state:
    st.session_state.current_customer = None
if 'base_risk' not in st.session_state:
    st.session_state.base_risk = None


# ==========================================
# 2. MODEL YÜKLEME (CACHE)
# ==========================================
@st.cache_resource
def load_local_model():
    try:
        pack = sio.load('churn_thesis_model.skops')
        return pack['model'], pack['scaler'], pack['features']
    except Exception as e:
        st.error(f"Model dosyası yüklenemedi: {e}")
        return None, None, None

local_model, local_scaler, expected_features = load_local_model()

@st.cache_resource
def get_shap_explainer(_model):
    """
    SHAP model açıklayıcısını önbelleğe alır (caching).
    TreeExplainer hesaplaması maliyetli olduğundan her render işleminde baştan hesaplanmasını engeller.
    """
    return shap.TreeExplainer(_model)

# TAHMİN FONKSİYONU (API YERİNE BURAYI KULLANACAĞIZ)
def make_prediction(data_dict):
    df_input = pd.DataFrame([data_dict])
    
    # Yeni Utils Fonksiyonu ile Ön İşleme
    scaled_input = preprocess_data(df_input, expected_features, local_scaler)

    # Tahmin
    prob = local_model.predict_proba(scaled_input)[0][1]
    pred = int(prob > 0.5)
    
    return {
        "churn_tahmini": pred,
        "churn_ihtimali": float(prob),
        "risk_seviyesi": "Yüksek" if prob > 0.7 else "Orta" if prob > 0.4 else "Düşük"
    }

def make_batch_prediction(df_input):
    """
    Toplu tahmin için optimize edilmiş tahmin fonksiyonu.
    """
    # Yeni Utils Fonksiyonu ile Ön İşleme
    scaled_input = preprocess_data(df_input, expected_features, local_scaler)

    # Tahmin
    probs = local_model.predict_proba(scaled_input)[:, 1]

    return probs

# ==========================================
# 3. GİRİŞ (LOGIN) EKRANI FONKSİYONU
# ==========================================
def login_screen():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🏦</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Kurumsal Yönetici Girişi</h3>", unsafe_allow_html=True)
        st.write("---")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if username == st.secrets["auth"]["username"] and password == st.secrets["auth"]["password"]:
                st.session_state.logged_in = True
                st.success("Giriş Başarılı!")
                st.rerun()
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre!")

# ==========================================
# 4. ANA PANEL (DASHBOARD) FONKSİYONU
# ==========================================
def main_dashboard():
    st.sidebar.title("Yönetici Menüsü")
    st.sidebar.info("Hoş Geldiniz, **Şube Müdürü**")
    if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🏦 Şube Müdürü Müşteri Risk Analiz Paneli")
    tab1, tab2, tab3 = st.tabs(["👤 Tekil Müşteri Analizi", "🧪 What-If Simülatörü", "📂 Toplu Analiz (CLTV Öncelikli)"])

    # --- SEKM 1: TEKİL MÜŞTERİ ANALİZİ ---
    with tab1:
        st.subheader("Müşteri Parametreleri")
        col_form1, col_form2, col_form3 = st.columns(3)
        with col_form1:
            credit_score = st.number_input("Kredi Notu", min_value=300, max_value=850, value=650)
            age = st.number_input("Yaş", min_value=18, max_value=100, value=40)
            tenure = st.number_input("Müşterilik Süresi (Yıl)", min_value=0, max_value=10, value=5)
        with col_form2:
            balance = st.number_input("Hesap Bakiyesi (€)", min_value=0.0, value=50000.0, step=1000.0)
            est_salary = st.number_input("Tahmini Maaş (€)", min_value=0.0, value=60000.0, step=1000.0)
            num_products = st.selectbox("Kullanılan Ürün Sayısı", [1, 2, 3, 4], index=1)
        with col_form3:
            geography = st.selectbox("Ülke", ["France", "Germany", "Spain"])
            gender = st.selectbox("Cinsiyet", ["Male", "Female"])
            has_cr_card = st.selectbox("Kredi Kartı Var mı?", [1, 0], format_func=lambda x: "Evet" if x == 1 else "Hayır")
            is_active = st.selectbox("Aktif Müşteri mi?", [1, 0], format_func=lambda x: "Evet" if x == 1 else "Hayır")

        if st.button("🔍 Risk Analizi Yap", use_container_width=True):
            customer_data = {
                "CreditScore": credit_score, "Geography": geography, "Gender": gender, "Age": age,
                "Tenure": tenure, "Balance": balance, "NumOfProducts": num_products,
                "HasCrCard": has_cr_card, "IsActiveMember": is_active, "EstimatedSalary": est_salary
            }

            with st.spinner("Yapay Zeka Hesaplarken Lütfen Bekleyin..."):
                # ARTIK API İSTEĞİ ATMIYORUZ, TAHMİNİ BURADA YAPIYORUZ
                result = make_prediction(customer_data)
                churn_probability = result["churn_ihtimali"] * 100
                st.session_state.current_customer = customer_data
                st.session_state.base_risk = churn_probability

                customer_value = balance + (est_salary * 0.20)
                expected_loss = customer_value * (churn_probability / 100)

                st.write("---")
                st.subheader("💰 Finansal Etki Analizi (CLTV)")
                fin_col1, fin_col2, fin_col3 = st.columns(3)
                fin_col1.metric(label="Müşterinin Bankaya Değeri", value=f"€{customer_value:,.2f}")
                fin_col2.metric(label="Ayrılma İhtimali", value=f"%{churn_probability:.1f}")
                fin_col3.metric(label="Beklenen Finansal Kayıp", value=f"€{expected_loss:,.2f}", delta="- Risk Tutarı", delta_color="inverse")

                st.write("---")
                res_col1, res_col2 = st.columns([1, 1])
                with res_col1:
                    st.subheader("📊 Model Çıktısı")
                    st.metric(label="Risk Kategorisi", value=result["risk_seviyesi"])
                    
                    # SHAP ANALİZİ (Önceden yaptığımız düzeltmelerle)
                    if local_model is not None:
                        st.markdown("### 💡 Neden Analizi (SHAP)")
                        df_input_shap = pd.DataFrame([customer_data])

                        # Utils ile Ön İşleme
                        scaled_input_shap = preprocess_data(df_input_shap, expected_features, local_scaler)
                        
                        explainer = get_shap_explainer(local_model)
                        shap_values = explainer.shap_values(scaled_input_shap, check_additivity=False)
                        
                        if isinstance(shap_values, list): shap_vals = shap_values[1][0]
                        else: shap_vals = shap_values[0, :, 1] if len(shap_values.shape) == 3 else shap_values[0]
                        
                        shap_vals = np.array(shap_vals).flatten()
                        sort_inds = np.argsort(np.abs(shap_vals))
                        sorted_features = np.array(expected_features)[sort_inds]
                        sorted_shap = shap_vals[sort_inds]
                        colors = ['salmon' if float(val) > 0 else 'lightgreen' for val in sorted_shap]

                        fig_shap = go.Figure(go.Bar(x=sorted_shap, y=sorted_features, orientation='h', marker_color=colors))
                        fig_shap.update_layout(xaxis_title="<- Riski Düşürenler | Riski Artıranlar ->", margin=dict(l=0, r=0, t=0, b=0), height=300)
                        st.plotly_chart(fig_shap, use_container_width=True)

                with res_col2:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number", value=churn_probability,
                        title={'text': "Ayrılma İhtimali (%)", 'font': {'size': 24}},
                        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "black"},
                               'steps': [{'range': [0, 40], 'color': "lightgreen"},
                                         {'range': [40, 70], 'color': "gold"},
                                         {'range': [70, 100], 'color': "salmon"}]}))
                    st.plotly_chart(fig_gauge, use_container_width=True)

    # --- SEKM 2: WHAT-IF SİMÜLATÖRÜ ---
    with tab2:
        if st.session_state.current_customer is not None:
            cust = st.session_state.current_customer
            base_risk = st.session_state.base_risk
            st.metric(label="Mevcut Durumdaki Ayrılma Riski", value=f"%{base_risk:.1f}")
            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                new_balance = st.number_input("Yeni Hesap Bakiyesi (€)", value=float(cust["Balance"]), step=1000.0, key="sim_bal")
                new_active = st.selectbox("Müşteriyi Aktif Hale Getir?", [1, 0], index=0 if cust["IsActiveMember"] == 1 else 1, key="sim_act")
            with sim_col2:
                new_crcard = st.selectbox("Kredi Kartı Kampanyası Tanımla?", [1, 0], index=0 if cust["HasCrCard"] == 1 else 1, key="sim_cr")
                new_products = st.slider("Ürün Sayısını Değiştir", 1, 4, value=cust["NumOfProducts"], key="sim_prod")

            if st.button("🔄 Değişim Senaryosunu Simüle Et", type="primary"):
                sim_data = cust.copy()
                sim_data.update({"Balance": new_balance, "IsActiveMember": new_active, "HasCrCard": new_crcard, "NumOfProducts": new_products})
                
                # SİMÜLASYONDA DA YEREL TAHMİN KULLANILIYOR
                res_sim = make_prediction(sim_data)
                new_risk = res_sim["churn_ihtimali"] * 100
                diff = new_risk - base_risk
                if diff < 0: st.metric(label="Yeni Risk", value=f"%{new_risk:.1f}", delta=f"{diff:.1f} Puan", delta_color="normal")
                else: st.metric(label="Yeni Risk", value=f"%{new_risk:.1f}", delta=f"+{diff:.1f} Puan", delta_color="inverse")
        else:
            st.warning("Lütfen önce 'Tekil Müşteri Analizi' sekmesinden bir analiz yapın.")

    # --- SEKM 3: TOPLU MÜŞTERİ YÜKLEME ---
    with tab3:
        st.subheader("📁 Finansal Odaklı Toplu Analiz")
        uploaded_file = st.file_uploader("Dosya Seçin", type=["csv"])
        if uploaded_file is not None:
            MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error("❌ Yüklenen dosya boyutu çok büyük! Maksimum 5MB yükleyebilirsiniz.")
            else:
                try:
                    df = pd.read_csv(uploaded_file)

                    required_columns = [
                        "CreditScore", "Geography", "Gender", "Age", "Tenure",
                        "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
                        "EstimatedSalary"
                    ]
                    missing_columns = [col for col in required_columns if col not in df.columns]

                    if missing_columns:
                        st.error(f"❌ Yüklenen dosyada eksik sütunlar var: {', '.join(missing_columns)}")
                    elif df.empty:
                        st.error("❌ Yüklenen dosya boş.")
                    elif len(df) > 10000:
                        st.error("❌ Dosya çok fazla satır içeriyor. Lütfen en fazla 10.000 satırlık bir dosya yükleyin.")
                    else:
                        if st.button("🚀 Tüm Listeyi Analiz Et ve Önceliklendir", use_container_width=True):
                            progress_bar = st.progress(0)

                            # Vektörel işlemlerle toplu tahmin ve hesaplamalar
                            df_input = df[required_columns].copy()

                            probs = make_batch_prediction(df_input)

                            c_values = df["Balance"] + (df["EstimatedSalary"] * 0.20)
                            exp_losses = c_values * probs

                            def get_risk_level(p):
                                if p > 0.7: return "Yüksek"
                                if p > 0.4: return "Orta"
                                return "Düşük"

                            risk_levels = [get_risk_level(p) for p in probs]
                            customer_ids = df["CustomerId"] if "CustomerId" in df.columns else df.index

                            results_df = pd.DataFrame({
                                "Müşteri ID": customer_ids,
                                "Risk (%)": np.round(probs * 100, 2),
                                "Risk Seviyesi": risk_levels,
                                "Müşteri Değeri (€)": np.round(c_values, 2),
                                "Beklenen Kayıp (€)": np.round(exp_losses, 2)
                            })

                            progress_bar.progress(1.0)

                            results_df = results_df.sort_values(by="Beklenen Kayıp (€)", ascending=False).reset_index(drop=True)
                            def color_risk(val): return f"color: {'red' if 'Yüksek' in str(val) else 'orange' if 'Orta' in str(val) else 'green'}"
                            styled_df = results_df.style.map(color_risk, subset=['Risk Seviyesi']).format({"Müşteri Değeri (€)": "{:,.2f}", "Beklenen Kayıp (€)": "{:,.2f}"})
                            st.success("✅ Analiz tamamlandı!")
                            st.dataframe(styled_df, use_container_width=True)
                            csv = results_df.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Analiz Raporunu İndir", data=csv, file_name='finansal_churn_raporu.csv', mime='text/csv')
                except Exception as e:
                    st.error(f"❌ Dosya okunurken bir hata oluştu: {e}")

# --- AKIŞ KONTROLÜ ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_dashboard()
