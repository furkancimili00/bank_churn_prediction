import os
import ast
import re

# Additional translations to inject into TRANSLATIONS (both tr and en)
NEW_TRANSLATIONS = {
    # tab_audit_logs.py
    'audit_no_logs': {'tr': 'Henüz denetim kaydi bulunmuyor.', 'en': 'No audit logs found yet.'},
    'audit_cleared': {'tr': 'Denetim logu temizlendi.', 'en': 'Audit log cleared.'},
    'audit_btn_clear': {'tr': '??? Denetim Logunu Temizle', 'en': '??? Clear Audit Log'},
    'audit_dist': {'tr': '### ?? Olay Türü Dagilimi', 'en': '### ?? Event Type Distribution'},
    'audit_recent': {'tr': '### ?? Son Kayitlar', 'en': '### ?? Recent Records'},
    'audit_desc': {'tr': 'Sistemde gerçeklesen tüm islemlerin zaman damgali kayitlari.', 'en': 'Time-stamped records of all operations in the system.'},
    'audit_num_logs': {'tr': 'Gösterilecek kayit sayisi:', 'en': 'Number of records to show:'},
    'audit_title': {'tr': '?? Denetim Günlügü (Audit Log)', 'en': '?? Audit Log'},
    
    # tab_drift.py
    'drift_desc': {'tr': 'Yeni yüklediginiz veriyi egitim verisine kiyaslayin. PSI ve KS testleri ile dagilim kaymalarini tespit edin.', 'en': 'Compare newly loaded data with training data. Detect distribution shifts via PSI and KS tests.'},
    'drift_no_ref': {'tr': '?? Referans veri seti (Churn_Modelling.csv) bulunamadi.', 'en': '?? Reference dataset (Churn_Modelling.csv) not found.'},
    'drift_upload_req': {'tr': '?? Lütfen karsilastirmak için bir CSV dosyasi yükleyin.', 'en': '?? Please upload a CSV file for comparison.'},
    'drift_no_num_cols': {'tr': 'Ortak sayisal sütun bulunamadi.', 'en': 'No common numeric columns found.'},
    'drift_dist_comp': {'tr': '### ?? Dagilim Karsilastirmalari', 'en': '### ?? Distribution Comparisons'},
    'drift_title': {'tr': '?? Veri Drift Analizi', 'en': '?? Data Drift Analysis'},
    'drift_upload': {'tr': 'Karsilastirilacak CSV Dosyasi Yükleyin', 'en': 'Upload CSV for Comparison'},
    
    # tab_eda.py
    'eda_feat_dist': {'tr': '### ?? Özellik Dagilimlari', 'en': '### ?? Feature Distributions'},
    'eda_title': {'tr': '?? Kesifsel Veri Analizi (EDA)', 'en': '?? Exploratory Data Analysis (EDA)'},
    'eda_box': {'tr': '### ?? Churn Karsilastirmali Box Plot', 'en': '### ?? Churn Comparative Box Plot'},
    'eda_need_data': {'tr': 'Lütfen bir veri kaynagi seçin veya CSV dosyasi yükleyin.', 'en': 'Please select a data source or upload a CSV file.'},
    'eda_corr': {'tr': '### ?? Korelasyon Matrisi', 'en': '### ?? Correlation Matrix'},
    'eda_desc': {'tr': 'Veri setini interaktif grafiklerle kesfedin. Varsayilan olarak egitim verisi kullanilir, veya kendi CSV dosyanizi yükleyebilirsiniz.', 'en': 'Explore dataset with interactive charts. Uses training data by default, or you can upload your own CSV.'},
    'eda_sunburst': {'tr': '### ?? Cografya ? Cinsiyet ? Churn (Sunburst)', 'en': '### ?? Geography ? Gender ? Churn (Sunburst)'},
    'eda_cat_churn': {'tr': '### ?? Kategorik Degiskenlere Göre Churn Orani', 'en': '### ?? Churn Rate by Categorical Variables'},
    'eda_overview': {'tr': '### ?? Genel Bakis', 'en': '### ?? Overview'},
    'eda_radio': {'tr': 'Veri Kaynagi Seçin:', 'en': 'Select Data Source:'},
    'eda_radio_default': {'tr': 'Varsayilan Veri Seti (Churn_Modelling.csv)', 'en': 'Default Dataset (Churn_Modelling.csv)'},
    'eda_radio_upload': {'tr': 'Kendi CSV Dosyami Yükle', 'en': 'Upload My Own CSV'},
    'eda_upload': {'tr': 'Veri Seti Yükleyin', 'en': 'Upload Dataset'},
    'eda_num_col': {'tr': 'Sayisal Sütun Seçin:', 'en': 'Select Numeric Column:'},
    'eda_cat_col': {'tr': 'Kategorik Sütun Seçin:', 'en': 'Select Categorical Column:'},
    
    # tab_fairness.py
    'fair_no_data': {'tr': '?? Varsayilan veri seti bulunamadi.', 'en': '?? Default dataset not found.'},
    'fair_title': {'tr': '?? Adillik ve Önyargi Analizi (Fairness/Bias)', 'en': '?? Fairness and Bias Analysis'},
    'fair_desc': {'tr': 'Modelin cinsiyet ve cografya bazinda adil tahmin yapip yapmadigini analiz edin. Tez hedefi: Disparate Impact < 1.2', 'en': 'Analyze whether the model makes fair predictions based on gender and geography. Thesis Target: Disparate Impact < 1.2'},
    'fair_summary': {'tr': '### ?? Adillik Özet Raporu', 'en': '### ?? Fairness Summary Report'},
    'fair_no_model': {'tr': '? Model yüklenemedi.', 'en': '? Model could not be loaded.'},
    
    # tab_management_report.py
    'report_req': {'tr': \"?? Lütfen önce 'Toplu Analiz' sekmesinden bir CSV dosyasi yükleyerek analiz yapin. Rapor bu veriler üzerinden olusturulacaktir.\", 'en': \"?? Please upload a CSV from 'Batch Analysis' first. Report uses this data.\"},
    'report_btn': {'tr': '?? Rapor Olustur', 'en': '?? Generate Report'},
    'report_title': {'tr': '?? Yönetim Raporu (RAG)', 'en': '?? Management Report (RAG)'},
    'report_ready': {'tr': 'Toplu analiz verileri hazir. Asagidaki butona basarak yönetim raporunu olusturabilirsiniz.', 'en': 'Batch data ready. Click the button below to generate the management report.'},
    
    # tab_performance.py
    'perf_no_model': {'tr': '? Model yüklenemedi. Model performansi gösterilemiyor.', 'en': '? Model could not be loaded. Performance cannot be displayed.'},
    'perf_desc': {'tr': 'Egitilmis XGBoost modelinin performans metriklerini, tez hedefleriyle karsilastirmali olarak inceleyin.', 'en': 'Review trained XGBoost model metrics against thesis goals.'},
    'perf_feat_imp': {'tr': '### ?? Özellik Önem Siralamasi', 'en': '### ?? Feature Importance'},
    'perf_roc': {'tr': '### ?? ROC Egrisi', 'en': '### ?? ROC Curve'},
    'perf_no_feat_imp': {'tr': 'Bu model Feature Importance desteklemiyor.', 'en': 'This model does not support Feature Importance.'},
    'perf_no_data': {'tr': '?? Varsayilan veri seti (Churn_Modelling.csv) bulunamadi.', 'en': '?? Default dataset (Churn_Modelling.csv) not found.'},
    'perf_err_metrics': {'tr': 'Model metrikleri hesaplanamadi. Lütfen veri setini kontrol edin.', 'en': 'Metrics could not be calculated. Please check dataset.'},
    'perf_pr': {'tr': '### ?? Precision-Recall Egrisi', 'en': '### ?? Precision-Recall Curve'},
    'perf_title': {'tr': '?? Model Performans Izleme', 'en': '?? Model Performance Monitoring'},
    'perf_cm': {'tr': '### ?? Karisiklik Matrisi', 'en': '### ?? Confusion Matrix'},
    'perf_target': {'tr': '### ?? Tez Hedefleri Karsilastirmasi', 'en': '### ?? Thesis Goals Comparison'},
    
    # tab_privacy.py
    'priv_title': {'tr': '?? Veri Gizliligi ve Anonimlestirme (KVKK/GDPR)', 'en': '?? Data Privacy and Anonymization (KVKK/GDPR)'},
    'priv_preview': {'tr': '### ??? Anonimlestirilmis Veri Önizlemesi (Ilk 10 Satir)', 'en': '### ??? Anonymized Data Preview (First 10 Rows)'},
    'priv_report': {'tr': '### ?? Gizlilik Raporu', 'en': '### ?? Privacy Report'},
    'priv_method': {'tr': 'Maskeleme Yöntemi Seçin:', 'en': 'Select Masking Method:'},
    'priv_btn': {'tr': '??? Anonimlestir ve Indir', 'en': '??? Anonymize and Download'},
    'priv_no_pii': {'tr': '?? Otomatik PII tespiti yapilamadi. Manuel sütun seçebilirsiniz.', 'en': '?? Automatic PII detection failed. You can select manually.'},
    'priv_desc': {'tr': 'CSV dosyanizdaki kisisel verileri (ad, soyad, müsteri ID) otomatik tespit edip maskeleyerek KVKK/GDPR uyumlu hale getirin.', 'en': 'Automatically detect and mask PII (name, ID) in your CSV to make it KVKK/GDPR compliant.'},
    'priv_upload': {'tr': 'Müsteri Verisi Içeren CSV Yükleyin', 'en': 'Upload CSV with Customer Data'},
    'priv_manual': {'tr': 'Manuel Maskelenecek Ek Sütunlar:', 'en': 'Additional Columns to Mask Manually:'},
    'priv_ready': {'tr': 'Anonimlestirme islemi basarili! Dosyayi indirebilirsiniz.', 'en': 'Anonymization successful! You can download the file.'},
    'priv_dl': {'tr': 'Anonimlestirilmis_Veri.csv', 'en': 'Anonymized_Data.csv'},
    
    # tab_profile_card.py
    'prof_desc': {'tr': 'Tekil Analiz sekmesinden analiz yapildiktan sonra, müsterinin tüm bilgileri, risk detaylari ve benzer müsteriler burada görüntülenir.', 'en': 'After performing Single Analysis, full customer profile, risk details and similar customers are displayed here.'},
    'prof_num': {'tr': 'Gösterilecek benzer müsteri sayisi:', 'en': 'Number of similar customers to show:'},
    'prof_shap': {'tr': '### ?? SHAP Waterfall Analizi', 'en': '### ?? SHAP Waterfall Analysis'},
    'prof_title': {'tr': '?? Müsteri 360° Profil Karti', 'en': '?? Customer 360° Profile Card'},
    'prof_no_shap': {'tr': 'SHAP Waterfall hesaplanamadi.', 'en': 'SHAP Waterfall could not be calculated.'},
    'prof_req': {'tr': \"?? Lütfen önce '?? Tekil Analiz' sekmesinden bir müsteri analizi yapin.\", 'en': \"?? Please analyze a customer in '?? Single Analysis' first.\"},
    'prof_history': {'tr': '### ?? Oturum Içi Risk Analizi Geçmisi', 'en': '### ?? In-Session Risk Analysis History'},
    'prof_no_sim_data': {'tr': 'Veri seti bulunamadigi için benzer müsteriler gösterilemiyor.', 'en': 'Cannot show similar customers because dataset is missing.'},
    'prof_sim_cust': {'tr': '### ?? Benzer Profilli Müsteriler', 'en': '### ?? Cust. with Similar Profiles'},
    
    # tab_segmentation.py
    'seg_no_data': {'tr': '?? Varsayilan veri seti bulunamadi.', 'en': '?? Default dataset not found.'},
    'seg_rate': {'tr': '### ?? Segment Bazinda Churn Orani', 'en': '### ?? Churn Rate by Segment'},
    'seg_btn': {'tr': '?? Segmentasyonu Baslat', 'en': '?? Start Segmentation'},
    'seg_desc': {'tr': 'Müsterilerinizi davranis ve demografik özelliklerine göre otomatik segmentlere ayirin. Her segmentin risk profilini ve özelliklerini kesfedin.', 'en': 'Automatically segment customers based on behavioral and demographic traits. Explore each segment risk profile.'},
    'seg_radar': {'tr': '### ??? Segment Profilleri (Radar)', 'en': '### ??? Segment Profiles (Radar)'},
    'seg_summary': {'tr': '### ?? Segment Özet Tablosu', 'en': '### ?? Segment Summary Table'},
    'seg_title': {'tr': '?? Müsteri Segmentasyonu (K-Means Kümeleme)', 'en': '?? Customer Segmentation (K-Means Clustering)'},
    'seg_k': {'tr': 'Küme Sayisini Seçin (k):', 'en': 'Select Number of Clusters (k):'},
    'seg_pca': {'tr': '### ?? PCA Kümeleme Görsellestirmesi', 'en': '### ?? PCA Cluster Visualization'},
    
    # tab_whatif_simulator.py
    'wi_fin': {'tr': '#### Finansal Durum', 'en': '#### Financial Status'},
    'wi_desc': {'tr': 'Asagidaki kaydiricilar ve seçeneklerle müsteri özelliklerini degistirerek ayrilma ihtimaline olan etkisini anlik olarak gözlemleyebilirsiniz.', 'en': 'Tweak customer features below to immediately see the impact on churn probability.'},
    'wi_active': {'tr': 'Müsteriyi Aktif Hale Getir?', 'en': 'Make Customer Active?'},
    'wi_results': {'tr': '?? Simülasyon Sonuçlari', 'en': '?? Simulation Results'},
    'wi_bank': {'tr': '#### Banka Ürün Kullanimi & Aktivite', 'en': '#### Bank Product T& Activity'},
    'wi_sal': {'tr': 'Yeni Tahmini Maas (€)', 'en': 'New Est. Salary (€)'},
    'wi_prod': {'tr': 'Ürün Sayisini Degistir', 'en': 'Change Product Amount'},
    'wi_cc': {'tr': 'Kredi Karti Kampanyasi Tanimla?', 'en': 'Add Credit Card Campaign?'},
    'wi_req': {'tr': \"Lütfen önce 'Tekil Müsteri Analizi' sekmesinden bir analiz yapin.\", 'en': \"Please do an analysis in 'Single Customer Analysis' first.\"},
    'wi_title': {'tr': '?? Müsteri Parametreleri Degisim Simülatörü', 'en': '?? Customer Parameter Change Simulator'},
    'wi_bal': {'tr': 'Yeni Hesap Bakiyesi (€)', 'en': 'New Account Balance (€)'},
    'wi_btn': {'tr': '?? Degisim Senaryosunu Simüle Et', 'en': '?? Simulate Scenario'}
}

# 1. Update ui/i18n.py
with open('ui/i18n.py', 'r', encoding='utf-8') as f:
    i18n_content = f.read()

# We need to insert keys into 'tr' and 'en'
idx_tr_end = i18n_content.find('    },\n    \"en\":')
tr_part = i18n_content[:idx_tr_end]
en_part = i18n_content[idx_tr_end:]
idx_en_end = en_part.rfind('    }')

new_tr_str = \",\\n\" + \",\\n\".join([f'        \"{k}\": {repr(v[\"tr\"])}' for k,v in NEW_TRANSLATIONS.items()])
new_en_str = \",\\n\" + \",\\n\".join([f'        \"{k}\": {repr(v[\"en\"])}' for k,v in NEW_TRANSLATIONS.items()])

if 'audit_no_logs' not in i18n_content:
    updated_i18n = tr_part + new_tr_str + en_part[:idx_en_end] + new_en_str + en_part[idx_en_end:]
    with open('ui/i18n.py', 'w', encoding='utf-8') as f:
        f.write(updated_i18n)

# 2. Update tab files with mappings
MAPPING = {v['tr']: f't(\"{k}\")' for k,v in NEW_TRANSLATIONS.items()}

import glob

for fp in glob.glob('ui/tabs/*.py'):
    with open(fp, 'r', encoding='utf-8') as f:
        code = f.read()

    original_code = code

    # Add import if missing
    if 'from ui.i18n import t' not in code:
        code = 'from ui.i18n import t\\n' + code

    # literal replace
    for tr_val, t_call in MAPPING.items():
        # Replace occurrences in code.
        # Careful with quotes. It could be \" or \'
        q1 = f'\"{tr_val}\"'
        q2 = f\"'{tr_val}'\"
        
        code = code.replace(q1, t_call).replace(q2, t_call)
    
    if code != original_code:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(code)

print(\"All translations applied!\")
