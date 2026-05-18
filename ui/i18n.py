import streamlit as st

from typing import Dict, Any



TRANSLATIONS: Dict[str, Dict[str, str]] = {

    "tr": {

        "tab_single": "👤 Tekil Analiz",

        "tab_whatif": "🧪 What-If",

        "tab_batch": "📂 Toplu Analiz",

        "tab_report": "📝 Yönetim Raporu",

        "tab_eda": "📈 EDA",

        "tab_perf": "🏆 Performans",

        "tab_segment": "🎯 Segmentasyon",

        "tab_fair": "⚖️ Adillik",

        "tab_profile": "👤 Profil Kartı",

        "tab_privacy": "🔒 Gizlilik",

        "tab_drift": "📉 Drift Analizi",

        "tab_audit": "📜 Denetim Günlüğü",

        "login_title": "Kurumsal Yönetici Girişi",

        "username": "Kullanıcı Adı",

        "password": "Şifre",

        "login_btn": "Sisteme Giriş Yap",

        "login_success": "Giriş başarılı.",

        "login_error": "Hatalı kullanıcı adı veya şifre.",

        "menu_title": "Yönetici Menüsü",

        "welcome": "Hoş geldiniz,",

        "manager": "Şube Müdürü",

        "about": "ℹ️ Uygulama Hakkında",

        "about_desc1": "Bu panel, müşteri terk riskini analiz etmek, simüle etmek ve toplu değerlendirmeler yapmak için geliştirilmiştir.",

        "about_desc2": "Yapay zeka destekli tahmin ve kampanya öneri sistemleri içerir.",

        "metrics": "📊 Genel Metrikler",

        "sys_status": "Sistem Durumu",

        "active": "Aktif",

        "model_loaded": "Model Yüklü",

        "logout": "🚪 Güvenli Çıkış Yap",

        "project_about": "🎓 Proje Hakkında",

        "main_title": "🏦 Şube Müdürü Müşteri Risk Analiz Paneli",

        

        "batch_title": "📂 Toplu Müşteri Analizi ve Önceliklendirme",

        "batch_desc": "Müşteri verilerinizi içeren CSV dosyasını yükleyerek toplu risk analizi yapabilir ve beklenen finansal kayba göre önceliklendirme alabilirsiniz.",

        "batch_file_limit": "Dosya boyutu çok büyük! Maksimum 5MB yüklenebilir.",

        "batch_upload_label": "Müşteri Verisi Yükleyin (CSV)",

        "batch_upload_help": "Max 5MB",

        "batch_error": "Geçersiz dosya yüklemesi.",

        

        "single_params": "📋 Müşteri Parametreleri",

        "single_analyze": "🔍 Risk Analizi Yap",

        "single_credit_score": "Kredi Notu",

        "single_age": "Yaş",

        "single_tenure": "Müşterilik Süresi (Yıl)",

        "single_balance": "Hesap Bakiyesi (€)",

        "single_salary": "Tahmini Maaş (€)",

        "single_products": "Kullanılan Ürün Sayısı",

        "single_country": "Ülke",

        "single_gender": "Cinsiyet",

        "single_credit_card": "Kredi Kartı Var mı?",

        "single_active": "Aktif Müşteri mi?",

        "single_yes": "Evet",

        "single_no": "Hayır",

        "analysis_results": "Analiz Sonuçları",

        "status": "Durum:",
        "audit_no_logs": "Henüz denetim kaydı bulunmuyor.",
        "audit_cleared": "Denetim logu temizlendi.",
        "audit_btn_clear": "🗑️ Denetim Logunu Temizle",
        "audit_dist": "### 📊 Olay Türü Dağılımı",
        "audit_recent": "### 📝 Son Kayıtlar",
        "audit_desc": "Sistemde gerçekleşen tüm işlemlerin zaman damgalı kayıtları.",
        "audit_num_logs": "Gösterilecek kayıt sayısı:",
        "audit_title": "📜 Denetim Günlüğü (Audit Log)",
        "drift_desc": "Yeni yüklediğiniz veriyi eğitim verisine kıyaslayın. PSI ve KS testleri ile dağılım kaymalarını tespit edin.",
        "drift_no_ref": "⚠️ Referans veri seti (Churn_Modelling.csv) bulunamadı.",
        "drift_upload_req": "📄 Lütfen karşılaştırmak için bir CSV dosyası yükleyin.",
        "drift_no_num_cols": "Ortak sayısal sütun bulunamadı.",
        "drift_dist_comp": "### 📊 Dağılım Karşılaştırmaları",
        "drift_title": "📉 Veri Drift Analizi",
        "drift_upload": "Karşılaştırılacak CSV Dosyası Yükleyin",
        "eda_feat_dist": "### 📊 Özellik Dağılımları",
        "eda_title": "📈 Keşifsel Veri Analizi (EDA)",
        "eda_box": "### 📦 Churn Karşılaştırmalı Box Plot",
        "eda_need_data": "Lütfen bir veri kaynağı seçin veya CSV dosyası yükleyin.",
        "eda_corr": "### 🔗 Korelasyon Matrisi",
        "eda_desc": "Veri setini interaktif grafiklerle keşfedin. Varsayılan olarak eğitim verisi kullanılır, veya kendi CSV dosyanızı yükleyebilirsiniz.",
        "eda_sunburst": "### 🌐 Coğrafya → Cinsiyet → Churn (Sunburst)",
        "eda_cat_churn": "### 📋 Kategorik Değişkenlere Göre Churn Oranı",
        "eda_overview": "### 📊 Genel Bakış",
        "eda_radio": "Veri Kaynağı Seçin:",
        "eda_radio_default": "Varsayılan Veri Seti (Churn_Modelling.csv)",
        "eda_radio_upload": "Kendi CSV Dosyamı Yükle",
        "eda_upload": "Veri Seti Yükleyin",
        "eda_num_col": "Sayısal Sütun Seçin:",
        "eda_cat_col": "Kategorik Sütun Seçin:",
        "fair_no_data": "⚠️ Varsayılan veri seti bulunamadı.",
        "fair_title": "⚖️ Adillik ve Önyargı Analizi (Fairness/Bias)",
        "fair_desc": "Modelin cinsiyet ve coğrafya bazında adil tahmin yapıp yapmadığını analiz edin. Tez hedefi: Disparate Impact < 1.2",
        "fair_summary": "### 📋 Adillik Özet Raporu",
        "fair_no_model": "❌ Model yüklenemedi.",
        "report_req": "⚠️ Lütfen önce 'Toplu Analiz' sekmesinden bir CSV dosyası yükleyerek analiz yapın. Rapor bu veriler üzerinden oluşturulacaktır.",
        "report_btn": "📊 Rapor Oluştur",
        "report_title": "📝 Yönetim Raporu (RAG)",
        "report_ready": "Toplu analiz verileri hazır. Aşağıdaki butona basarak yönetim raporunu oluşturabilirsiniz.",
        "perf_no_model": "❌ Model yüklenemedi. Model performansı gösterilemiyor.",
        "perf_desc": "Eğitilmiş XGBoost modelinin performans metriklerini, tez hedefleriyle karşılaştırmalı olarak inceleyin.",
        "perf_feat_imp": "### 🎯 Özellik Önem Sıralaması",
        "perf_roc": "### 📈 ROC Eğrisi",
        "perf_no_feat_imp": "Bu model Feature Importance desteklemiyor.",
        "perf_no_data": "⚠️ Varsayılan veri seti (Churn_Modelling.csv) bulunamadı.",
        "perf_err_metrics": "Model metrikleri hesaplanamadı. Lütfen veri setini kontrol edin.",
        "perf_pr": "### 📉 Precision-Recall Eğrisi",
        "perf_title": "🏆 Model Performans İzleme",
        "perf_cm": "### 🔢 Karışıklık Matrisi",
        "perf_target": "### 📋 Tez Hedefleri Karşılaştırması",
        "priv_title": "🔒 Veri Gizliliği ve Anonimleştirme (KVKK/GDPR)",
        "priv_preview": "### 👁️ Anonimleştirilmiş Veri Önizlemesi (İlk 10 Satır)",
        "priv_report": "### 📋 Gizlilik Raporu",
        "priv_method": "Maskeleme Yöntemi Seçin:",
        "priv_btn": "🛡️ Anonimleştir ve İndir",
        "priv_no_pii": "⚠️ Otomatik PII tespiti yapılamadı. Manuel sütun seçebilirsiniz.",
        "priv_desc": "CSV dosyanızdaki kişisel verileri (ad, soyad, müşteri ID) otomatik tespit edip maskeleyerek KVKK/GDPR uyumlu hale getirin.",
        "priv_upload": "Müşteri Verisi İçeren CSV Yükleyin",
        "priv_manual": "Manuel Maskelenecek Ek Sütunlar:",
        "priv_ready": "Anonimleştirme işlemi başarılı! Dosyayı indirebilirsiniz.",
        "priv_dl": "Anonimleştirilmiş_Veri.csv",
        "prof_desc": "Tekil Analiz sekmesinden analiz yapıldıktan sonra, müşterinin tüm bilgileri, risk detayları ve benzer müşteriler burada görüntülenir.",
        "prof_num": "Gösterilecek benzer müşteri sayısı:",
        "prof_shap": "### 🌊 SHAP Waterfall Analizi",
        "prof_title": "👤 Müşteri 360° Profil Kartı",
        "prof_no_shap": "SHAP Waterfall hesaplanamadı.",
        "prof_req": "⚠️ Lütfen önce '👤 Tekil Analiz' sekmesinden bir müşteri analizi yapın.",
        "prof_history": "### 📈 Oturum İçi Risk Analizi Geçmişi",
        "prof_no_sim_data": "Veri seti bulunamadığı için benzer müşteriler gösterilemiyor.",
        "prof_sim_cust": "### 🔍 Benzer Profilli Müşteriler",
        "seg_no_data": "⚠️ Varsayılan veri seti bulunamadı.",
        "seg_rate": "### 📊 Segment Bazında Churn Oranı",
        "seg_btn": "🚀 Segmentasyonu Başlat",
        "seg_desc": "Müşterilerinizi davranış ve demografik özelliklerine göre otomatik segmentlere ayırın. Her segmentin risk profilini ve özelliklerini keşfedin.",
        "seg_radar": "### 🕸️ Segment Profilleri (Radar)",
        "seg_summary": "### 📋 Segment Özet Tablosu",
        "seg_title": "🎯 Müşteri Segmentasyonu (K-Means Kümeleme)",
        "seg_k": "Küme Sayısını Seçin (k):",
        "seg_pca": "### 📊 PCA Kümeleme Görselleştirmesi",
        "wi_fin": "#### Finansal Durum",
        "wi_desc": "Aşağıdaki kaydırıcılar ve seçeneklerle müşteri özelliklerini değiştirerek ayrılma ihtimaline olan etkisini anlık olarak gözlemleyebilirsiniz.",
        "wi_active": "Müşteriyi Aktif Hale Getir?",
        "wi_results": "📈 Simülasyon Sonuçları",
        "wi_bank": "#### Banka Ürün Kullanımı & Aktivite",
        "wi_sal": "Yeni Tahmini Maaş (€)",
        "wi_prod": "Ürün Sayısını Değiştir",
        "wi_cc": "Kredi Kartı Kampanyası Tanımla?",
        "wi_req": "Lütfen önce 'Tekil Müşteri Analizi' sekmesinden bir analiz yapın.",
        "wi_title": "🧪 Müşteri Parametreleri Değişim Simülatörü",
        "wi_bal": "Yeni Hesap Bakiyesi (€)",
        "wi_btn": "🔄 Değişim Senaryosunu Simüle Et"

    },

    "en": {

        "tab_single": "👤 Single Analysis",

        "tab_whatif": "🧪 What-If",

        "tab_batch": "📂 Batch Analysis",

        "tab_report": "📝 Management Report",

        "tab_eda": "📈 EDA",

        "tab_perf": "🏆 Performance",

        "tab_segment": "🎯 Segmentation",

        "tab_fair": "⚖️ Fairness",

        "tab_profile": "👤 Profile Card",

        "tab_privacy": "🔒 Privacy",

        "tab_drift": "📉 Drift Analysis",

        "tab_audit": "📜 Audit Logs",

        "login_title": "Corporate Admin Login",

        "username": "Username",

        "password": "Password",

        "login_btn": "Login to System",

        "login_success": "Login successful.",

        "login_error": "Invalid username or password.",

        "menu_title": "Manager Menu",

        "welcome": "Welcome,",

        "manager": "Branch Manager",

        "about": "ℹ️ About Application",

        "about_desc1": "This dashboard is developed to analyze, simulate, and perform batch evaluations of customer churn risk.",

        "about_desc2": "It includes AI-supported prediction and campaign recommendation systems.",

        "metrics": "📊 General Metrics",

        "sys_status": "System Status",

        "active": "Active",

        "model_loaded": "Model Loaded",

        "logout": "🚪 Secure Logout",

        "project_about": "🎓 About Project",

        "main_title": "🏦 Branch Manager Customer Risk Analysis Dashboard",

        

        "batch_title": "📂 Batch Customer Analysis & Prioritization",

        "batch_desc": "Upload your customer data CSV file to perform bulk risk analysis and get prioritization based on expected financial loss.",

        "batch_file_limit": "File size is too big! Maximum 5MB is allowed.",

        "batch_upload_label": "Upload Customer Data (CSV)",

        "batch_upload_help": "Max 5MB",

        "batch_error": "Invalid file upload.",

        

        "single_params": "📋 Customer Parameters",

        "single_analyze": "🔍 Run Risk Analysis",

        "single_credit_score": "Credit Score",

        "single_age": "Age",

        "single_tenure": "Tenure (Years)",

        "single_balance": "Account Balance (€)",

        "single_salary": "Estimated Salary (€)",

        "single_products": "Num Of Products",

        "single_country": "Geography",

        "single_gender": "Gender",

        "single_credit_card": "Has Credit Card?",

        "single_active": "Is Active Member?",

        "single_yes": "Yes",

        "single_no": "No",

        "analysis_results": "Analysis Results",

        "status": "Status:",
        "audit_no_logs": "No audit logs found yet.",
        "audit_cleared": "Audit log cleared.",
        "audit_btn_clear": "🗑️ Clear Audit Log",
        "audit_dist": "### 📊 Event Type Distribution",
        "audit_recent": "### 📝 Recent Records",
        "audit_desc": "Time-stamped records of all operations in the system.",
        "audit_num_logs": "Number of records to show:",
        "audit_title": "📜 Audit Log",
        "drift_desc": "Compare newly loaded data with training data. Detect distribution shifts via PSI and KS tests.",
        "drift_no_ref": "⚠️ Reference dataset (Churn_Modelling.csv) not found.",
        "drift_upload_req": "📄 Please upload a CSV file for comparison.",
        "drift_no_num_cols": "No common numeric columns found.",
        "drift_dist_comp": "### 📊 Distribution Comparisons",
        "drift_title": "📉 Data Drift Analysis",
        "drift_upload": "Upload CSV for Comparison",
        "eda_feat_dist": "### 📊 Feature Distributions",
        "eda_title": "📈 Exploratory Data Analysis (EDA)",
        "eda_box": "### 📦 Churn Comparative Box Plot",
        "eda_need_data": "Please select a data source or upload a CSV file.",
        "eda_corr": "### 🔗 Correlation Matrix",
        "eda_desc": "Explore dataset with interactive charts. Uses training data by default, or you can upload your own CSV.",
        "eda_sunburst": "### 🌐 Geography → Gender → Churn (Sunburst)",
        "eda_cat_churn": "### 📋 Churn Rate by Categorical Variables",
        "eda_overview": "### 📊 Overview",
        "eda_radio": "Select Data Source:",
        "eda_radio_default": "Default Dataset (Churn_Modelling.csv)",
        "eda_radio_upload": "Upload My Own CSV",
        "eda_upload": "Upload Dataset",
        "eda_num_col": "Select Numeric Column:",
        "eda_cat_col": "Select Categorical Column:",
        "fair_no_data": "⚠️ Default dataset not found.",
        "fair_title": "⚖️ Fairness and Bias Analysis",
        "fair_desc": "Analyze whether the model makes fair predictions based on gender and geography. Thesis Target: Disparate Impact < 1.2",
        "fair_summary": "### 📋 Fairness Summary Report",
        "fair_no_model": "❌ Model could not be loaded.",
        "report_req": "⚠️ Please upload a CSV from 'Batch Analysis' first. Report uses this data.",
        "report_btn": "📊 Generate Report",
        "report_title": "📝 Management Report (RAG)",
        "report_ready": "Batch data ready. Click the button below to generate the management report.",
        "perf_no_model": "❌ Model could not be loaded. Performance cannot be displayed.",
        "perf_desc": "Review trained XGBoost model metrics against thesis goals.",
        "perf_feat_imp": "### 🎯 Feature Importance",
        "perf_roc": "### 📈 ROC Curve",
        "perf_no_feat_imp": "This model does not support Feature Importance.",
        "perf_no_data": "⚠️ Default dataset (Churn_Modelling.csv) not found.",
        "perf_err_metrics": "Metrics could not be calculated. Please check dataset.",
        "perf_pr": "### 📉 Precision-Recall Curve",
        "perf_title": "🏆 Model Performance Monitoring",
        "perf_cm": "### 🔢 Confusion Matrix",
        "perf_target": "### 📋 Thesis Goals Comparison",
        "priv_title": "🔒 Data Privacy and Anonymization (KVKK/GDPR)",
        "priv_preview": "### 👁️ Anonymized Data Preview (First 10 Rows)",
        "priv_report": "### 📋 Privacy Report",
        "priv_method": "Select Masking Method:",
        "priv_btn": "🛡️ Anonymize and Download",
        "priv_no_pii": "⚠️ Automatic PII detection failed. You can select manually.",
        "priv_desc": "Automatically detect and mask PII (name, ID) in your CSV to make it KVKK/GDPR compliant.",
        "priv_upload": "Upload CSV with Customer Data",
        "priv_manual": "Additional Columns to Mask Manually:",
        "priv_ready": "Anonymization successful! You can download the file.",
        "priv_dl": "Anonymized_Data.csv",
        "prof_desc": "After performing Single Analysis, full customer profile, risk details and similar customers are displayed here.",
        "prof_num": "Number of similar customers to show:",
        "prof_shap": "### 🌊 SHAP Waterfall Analysis",
        "prof_title": "👤 Customer 360° Profile Card",
        "prof_no_shap": "SHAP Waterfall could not be calculated.",
        "prof_req": "⚠️ Please analyze a customer in '👤 Single Analysis' first.",
        "prof_history": "### 📈 In-Session Risk Analysis History",
        "prof_no_sim_data": "Cannot show similar customers because dataset is missing.",
        "prof_sim_cust": "### 🔍 Cust. with Similar Profiles",
        "seg_no_data": "⚠️ Default dataset not found.",
        "seg_rate": "### 📊 Churn Rate by Segment",
        "seg_btn": "🚀 Start Segmentation",
        "seg_desc": "Automatically segment customers based on behavioral and demographic traits. Explore each segment risk profile.",
        "seg_radar": "### 🕸️ Segment Profiles (Radar)",
        "seg_summary": "### 📋 Segment Summary Table",
        "seg_title": "🎯 Customer Segmentation (K-Means Clustering)",
        "seg_k": "Select Number of Clusters (k):",
        "seg_pca": "### 📊 PCA Cluster Visualization",
        "wi_fin": "#### Financial Status",
        "wi_desc": "Tweak customer features below to immediately see the impact on churn probability.",
        "wi_active": "Make Customer Active?",
        "wi_results": "📈 Simulation Results",
        "wi_bank": "#### Bank Product T& Activity",
        "wi_sal": "New Est. Salary (€)",
        "wi_prod": "Change Product Amount",
        "wi_cc": "Add Credit Card Campaign?",
        "wi_req": "Please do an analysis in 'Single Customer Analysis' first.",
        "wi_title": "🧪 Customer Parameter Change Simulator",
        "wi_bal": "New Account Balance (€)",
        "wi_btn": "🔄 Simulate Scenario"

    }

}



def init_i18n():

    if "lang" not in st.session_state:

        st.session_state["lang"] = "tr"

    if "theme" not in st.session_state:

        st.session_state["theme"] = "dark"



def t(key: str) -> str:

    lang = st.session_state.get("lang", "tr")

    return TRANSLATIONS.get(lang, TRANSLATIONS["tr"]).get(key, key)



def render_language_and_theme_toggles():

    st.sidebar.markdown("---")

    st.sidebar.subheader("⚙️ Ayarlar / Settings" if st.session_state.get("lang") == "tr" else "⚙️ Settings / Ayarlar")

    

    # Language Toggle

    lang_options = {"tr": "🇹🇷 Türkçe", "en": "🇬🇧 English"}

    current_lang_idx = 0 if st.session_state["lang"] == "tr" else 1

    

    selected_lang_label = st.sidebar.selectbox("Dil / Language", list(lang_options.values()), index=current_lang_idx)

    new_lang = "tr" if "Türkçe" in selected_lang_label else "en"

    

    if new_lang != st.session_state["lang"]:

        st.session_state["lang"] = new_lang

        st.rerun()



    # Theme Toggle

    def toggle_theme():

        st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"



    theme_label = "🌙 Dark Mode" if st.session_state["theme"] == "dark" else "☀️ Light Mode"

    st.sidebar.checkbox(theme_label, value=(st.session_state["theme"] == "dark"), on_change=toggle_theme)



    # Fixed CSS for avoiding coloring the file uploader widget directly or making it hard to see contrast.

    # Excluded specific Streamlit classes that handle data tables and file uploaders inside.

    if st.session_state["theme"] == "dark":

        css = """

        <style>

            [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; color: #FAFAFA !important; }

            [data-testid="stSidebar"] { background-color: #262730 !important; }

            [data-testid="stHeader"] { background-color: #0E1117 !important; }

            [data-testid="stFileUploaderDropzone"] { background-color: rgba(255,255,255,0.05) !important; color: #ffffff !important; }

        </style>

        """

    else:

        css = """

        <style>

            [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; color: #31333F !important; }

            [data-testid="stSidebar"] { background-color: #F0F2F6 !important; }

            [data-testid="stHeader"] { background-color: #FFFFFF !important; }

            [data-testid="stFileUploaderDropzone"] { background-color: rgba(0,0,0,0.05) !important; color: #31333f !important; }

        </style>

        """

    st.markdown(css, unsafe_allow_html=True)