import ast

NEW_TRANSLATIONS = {
    # tab_audit_logs.py
    'audit_no_logs': {'tr': 'Henüz denetim kaydı bulunmuyor.', 'en': 'No audit logs found yet.'},
    'audit_cleared': {'tr': 'Denetim logu temizlendi.', 'en': 'Audit log cleared.'},
    'audit_btn_clear': {'tr': '🗑️ Denetim Logunu Temizle', 'en': '🗑️ Clear Audit Log'},
    'audit_dist': {'tr': '### 📊 Olay Türü Dağılımı', 'en': '### 📊 Event Type Distribution'},
    'audit_recent': {'tr': '### 📝 Son Kayıtlar', 'en': '### 📝 Recent Records'},
    'audit_desc': {'tr': 'Sistemde gerçekleşen tüm işlemlerin zaman damgalı kayıtları.', 'en': 'Time-stamped records of all operations in the system.'},
    'audit_num_logs': {'tr': 'Gösterilecek kayıt sayısı:', 'en': 'Number of records to show:'},
    'audit_title': {'tr': '📜 Denetim Günlüğü (Audit Log)', 'en': '📜 Audit Log'},
    
    # tab_drift.py
    'drift_desc': {'tr': 'Yeni yüklediğiniz veriyi eğitim verisine kıyaslayın. PSI ve KS testleri ile dağılım kaymalarını tespit edin.', 'en': 'Compare newly loaded data with training data. Detect distribution shifts via PSI and KS tests.'},
    'drift_no_ref': {'tr': '⚠️ Referans veri seti (Churn_Modelling.csv) bulunamadı.', 'en': '⚠️ Reference dataset (Churn_Modelling.csv) not found.'},
    'drift_upload_req': {'tr': '📄 Lütfen karşılaştırmak için bir CSV dosyası yükleyin.', 'en': '📄 Please upload a CSV file for comparison.'},
    'drift_no_num_cols': {'tr': 'Ortak sayısal sütun bulunamadı.', 'en': 'No common numeric columns found.'},
    'drift_dist_comp': {'tr': '### 📊 Dağılım Karşılaştırmaları', 'en': '### 📊 Distribution Comparisons'},
    'drift_title': {'tr': '📉 Veri Drift Analizi', 'en': '📉 Data Drift Analysis'},
    'drift_upload': {'tr': 'Karşılaştırılacak CSV Dosyası Yükleyin', 'en': 'Upload CSV for Comparison'},
    
    # tab_eda.py
    'eda_feat_dist': {'tr': '### 📊 Özellik Dağılımları', 'en': '### 📊 Feature Distributions'},
    'eda_title': {'tr': '📈 Keşifsel Veri Analizi (EDA)', 'en': '📈 Exploratory Data Analysis (EDA)'},
    'eda_box': {'tr': '### 📦 Churn Karşılaştırmalı Box Plot', 'en': '### 📦 Churn Comparative Box Plot'},
    'eda_need_data': {'tr': 'Lütfen bir veri kaynağı seçin veya CSV dosyası yükleyin.', 'en': 'Please select a data source or upload a CSV file.'},
    'eda_corr': {'tr': '### 🔗 Korelasyon Matrisi', 'en': '### 🔗 Correlation Matrix'},
    'eda_desc': {'tr': 'Veri setini interaktif grafiklerle keşfedin. Varsayılan olarak eğitim verisi kullanılır, veya kendi CSV dosyanızı yükleyebilirsiniz.', 'en': 'Explore dataset with interactive charts. Uses training data by default, or you can upload your own CSV.'},
    'eda_sunburst': {'tr': '### 🌐 Coğrafya → Cinsiyet → Churn (Sunburst)', 'en': '### 🌐 Geography → Gender → Churn (Sunburst)'},
    'eda_cat_churn': {'tr': '### 📋 Kategorik Değişkenlere Göre Churn Oranı', 'en': '### 📋 Churn Rate by Categorical Variables'},
    'eda_overview': {'tr': '### 📊 Genel Bakış', 'en': '### 📊 Overview'},
    'eda_radio': {'tr': 'Veri Kaynağı Seçin:', 'en': 'Select Data Source:'},
    'eda_radio_default': {'tr': 'Varsayılan Veri Seti (Churn_Modelling.csv)', 'en': 'Default Dataset (Churn_Modelling.csv)'},
    'eda_radio_upload': {'tr': 'Kendi CSV Dosyamı Yükle', 'en': 'Upload My Own CSV'},
    'eda_upload': {'tr': 'Veri Seti Yükleyin', 'en': 'Upload Dataset'},
    'eda_num_col': {'tr': 'Sayısal Sütun Seçin:', 'en': 'Select Numeric Column:'},
    'eda_cat_col': {'tr': 'Kategorik Sütun Seçin:', 'en': 'Select Categorical Column:'},
    
    # tab_fairness.py
    'fair_no_data': {'tr': '⚠️ Varsayılan veri seti bulunamadı.', 'en': '⚠️ Default dataset not found.'},
    'fair_title': {'tr': '⚖️ Adillik ve Önyargı Analizi (Fairness/Bias)', 'en': '⚖️ Fairness and Bias Analysis'},
    'fair_desc': {'tr': 'Modelin cinsiyet ve coğrafya bazında adil tahmin yapıp yapmadığını analiz edin. Tez hedefi: Disparate Impact < 1.2', 'en': 'Analyze whether the model makes fair predictions based on gender and geography. Thesis Target: Disparate Impact < 1.2'},
    'fair_summary': {'tr': '### 📋 Adillik Özet Raporu', 'en': '### 📋 Fairness Summary Report'},
    'fair_no_model': {'tr': '❌ Model yüklenemedi.', 'en': '❌ Model could not be loaded.'},
    
    # tab_management_report.py
    'report_req': {'tr': "⚠️ Lütfen önce 'Toplu Analiz' sekmesinden bir CSV dosyası yükleyerek analiz yapın. Rapor bu veriler üzerinden oluşturulacaktır.", 'en': "⚠️ Please upload a CSV from 'Batch Analysis' first. Report uses this data."},
    'report_btn': {'tr': '📊 Rapor Oluştur', 'en': '📊 Generate Report'},
    'report_title': {'tr': '📝 Yönetim Raporu (RAG)', 'en': '📝 Management Report (RAG)'},
    'report_ready': {'tr': 'Toplu analiz verileri hazır. Aşağıdaki butona basarak yönetim raporunu oluşturabilirsiniz.', 'en': 'Batch data ready. Click the button below to generate the management report.'},
    
    # tab_performance.py
    'perf_no_model': {'tr': '❌ Model yüklenemedi. Model performansı gösterilemiyor.', 'en': '❌ Model could not be loaded. Performance cannot be displayed.'},
    'perf_desc': {'tr': 'Eğitilmiş XGBoost modelinin performans metriklerini, tez hedefleriyle karşılaştırmalı olarak inceleyin.', 'en': 'Review trained XGBoost model metrics against thesis goals.'},
    'perf_feat_imp': {'tr': '### 🎯 Özellik Önem Sıralaması', 'en': '### 🎯 Feature Importance'},
    'perf_roc': {'tr': '### 📈 ROC Eğrisi', 'en': '### 📈 ROC Curve'},
    'perf_no_feat_imp': {'tr': 'Bu model Feature Importance desteklemiyor.', 'en': 'This model does not support Feature Importance.'},
    'perf_no_data': {'tr': '⚠️ Varsayılan veri seti (Churn_Modelling.csv) bulunamadı.', 'en': '⚠️ Default dataset (Churn_Modelling.csv) not found.'},
    'perf_err_metrics': {'tr': 'Model metrikleri hesaplanamadı. Lütfen veri setini kontrol edin.', 'en': 'Metrics could not be calculated. Please check dataset.'},
    'perf_pr': {'tr': '### 📉 Precision-Recall Eğrisi', 'en': '### 📉 Precision-Recall Curve'},
    'perf_title': {'tr': '🏆 Model Performans İzleme', 'en': '🏆 Model Performance Monitoring'},
    'perf_cm': {'tr': '### 🔢 Karışıklık Matrisi', 'en': '### 🔢 Confusion Matrix'},
    'perf_target': {'tr': '### 📋 Tez Hedefleri Karşılaştırması', 'en': '### 📋 Thesis Goals Comparison'},
    
    # tab_privacy.py
    'priv_title': {'tr': '🔒 Veri Gizliliği ve Anonimleştirme (KVKK/GDPR)', 'en': '🔒 Data Privacy and Anonymization (KVKK/GDPR)'},
    'priv_preview': {'tr': '### 👁️ Anonimleştirilmiş Veri Önizlemesi (İlk 10 Satır)', 'en': '### 👁️ Anonymized Data Preview (First 10 Rows)'},
    'priv_report': {'tr': '### 📋 Gizlilik Raporu', 'en': '### 📋 Privacy Report'},
    'priv_method': {'tr': 'Maskeleme Yöntemi Seçin:', 'en': 'Select Masking Method:'},
    'priv_btn': {'tr': '🛡️ Anonimleştir ve İndir', 'en': '🛡️ Anonymize and Download'},
    'priv_no_pii': {'tr': '⚠️ Otomatik PII tespiti yapılamadı. Manuel sütun seçebilirsiniz.', 'en': '⚠️ Automatic PII detection failed. You can select manually.'},
    'priv_desc': {'tr': 'CSV dosyanızdaki kişisel verileri (ad, soyad, müşteri ID) otomatik tespit edip maskeleyerek KVKK/GDPR uyumlu hale getirin.', 'en': 'Automatically detect and mask PII (name, ID) in your CSV to make it KVKK/GDPR compliant.'},
    'priv_upload': {'tr': 'Müşteri Verisi İçeren CSV Yükleyin', 'en': 'Upload CSV with Customer Data'},
    'priv_manual': {'tr': 'Manuel Maskelenecek Ek Sütunlar:', 'en': 'Additional Columns to Mask Manually:'},
    'priv_ready': {'tr': 'Anonimleştirme işlemi başarılı! Dosyayı indirebilirsiniz.', 'en': 'Anonymization successful! You can download the file.'},
    'priv_dl': {'tr': 'Anonimleştirilmiş_Veri.csv', 'en': 'Anonymized_Data.csv'},
    
    # tab_profile_card.py
    'prof_desc': {'tr': 'Tekil Analiz sekmesinden analiz yapıldıktan sonra, müşterinin tüm bilgileri, risk detayları ve benzer müşteriler burada görüntülenir.', 'en': 'After performing Single Analysis, full customer profile, risk details and similar customers are displayed here.'},
    'prof_num': {'tr': 'Gösterilecek benzer müşteri sayısı:', 'en': 'Number of similar customers to show:'},
    'prof_shap': {'tr': '### 🌊 SHAP Waterfall Analizi', 'en': '### 🌊 SHAP Waterfall Analysis'},
    'prof_title': {'tr': '👤 Müşteri 360° Profil Kartı', 'en': '👤 Customer 360° Profile Card'},
    'prof_no_shap': {'tr': 'SHAP Waterfall hesaplanamadı.', 'en': 'SHAP Waterfall could not be calculated.'},
    'prof_req': {'tr': "⚠️ Lütfen önce '👤 Tekil Analiz' sekmesinden bir müşteri analizi yapın.", 'en': "⚠️ Please analyze a customer in '👤 Single Analysis' first."},
    'prof_history': {'tr': '### 📈 Oturum İçi Risk Analizi Geçmişi', 'en': '### 📈 In-Session Risk Analysis History'},
    'prof_no_sim_data': {'tr': 'Veri seti bulunamadığı için benzer müşteriler gösterilemiyor.', 'en': 'Cannot show similar customers because dataset is missing.'},
    'prof_sim_cust': {'tr': '### 🔍 Benzer Profilli Müşteriler', 'en': '### 🔍 Cust. with Similar Profiles'},
    
    # tab_segmentation.py
    'seg_no_data': {'tr': '⚠️ Varsayılan veri seti bulunamadı.', 'en': '⚠️ Default dataset not found.'},
    'seg_rate': {'tr': '### 📊 Segment Bazında Churn Oranı', 'en': '### 📊 Churn Rate by Segment'},
    'seg_btn': {'tr': '🚀 Segmentasyonu Başlat', 'en': '🚀 Start Segmentation'},
    'seg_desc': {'tr': 'Müşterilerinizi davranış ve demografik özelliklerine göre otomatik segmentlere ayırın. Her segmentin risk profilini ve özelliklerini keşfedin.', 'en': 'Automatically segment customers based on behavioral and demographic traits. Explore each segment risk profile.'},
    'seg_radar': {'tr': '### 🕸️ Segment Profilleri (Radar)', 'en': '### 🕸️ Segment Profiles (Radar)'},
    'seg_summary': {'tr': '### 📋 Segment Özet Tablosu', 'en': '### 📋 Segment Summary Table'},
    'seg_title': {'tr': '🎯 Müşteri Segmentasyonu (K-Means Kümeleme)', 'en': '🎯 Customer Segmentation (K-Means Clustering)'},
    'seg_k': {'tr': 'Küme Sayısını Seçin (k):', 'en': 'Select Number of Clusters (k):'},
    'seg_pca': {'tr': '### 📊 PCA Kümeleme Görselleştirmesi', 'en': '### 📊 PCA Cluster Visualization'},
    
    # tab_whatif_simulator.py
    'wi_fin': {'tr': '#### Finansal Durum', 'en': '#### Financial Status'},
    'wi_desc': {'tr': 'Aşağıdaki kaydırıcılar ve seçeneklerle müşteri özelliklerini değiştirerek ayrılma ihtimaline olan etkisini anlık olarak gözlemleyebilirsiniz.', 'en': 'Tweak customer features below to immediately see the impact on churn probability.'},
    'wi_active': {'tr': 'Müşteriyi Aktif Hale Getir?', 'en': 'Make Customer Active?'},
    'wi_results': {'tr': '📈 Simülasyon Sonuçları', 'en': '📈 Simulation Results'},
    'wi_bank': {'tr': '#### Banka Ürün Kullanımı & Aktivite', 'en': '#### Bank Product T& Activity'},
    'wi_sal': {'tr': 'Yeni Tahmini Maaş (€)', 'en': 'New Est. Salary (€)'},
    'wi_prod': {'tr': 'Ürün Sayısını Değiştir', 'en': 'Change Product Amount'},
    'wi_cc': {'tr': 'Kredi Kartı Kampanyası Tanımla?', 'en': 'Add Credit Card Campaign?'},
    'wi_req': {'tr': "Lütfen önce 'Tekil Müşteri Analizi' sekmesinden bir analiz yapın.", 'en': "Please do an analysis in 'Single Customer Analysis' first."},
    'wi_title': {'tr': '🧪 Müşteri Parametreleri Değişim Simülatörü', 'en': '🧪 Customer Parameter Change Simulator'},
    'wi_bal': {'tr': 'Yeni Hesap Bakiyesi (€)', 'en': 'New Account Balance (€)'},
    'wi_btn': {'tr': '🔄 Değişim Senaryosunu Simüle Et', 'en': '🔄 Simulate Scenario'}
}

with open('ui/i18n.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# We reliably extract TRANSLATIONS string
match = re.search(r'(TRANSLATIONS\s*:\s*Dict\[str,\s*Dict\[str,\s*str\]\]\s*=\s*\{\s*"tr"\s*:\s*\{.*?\n)(\s*\},\s*"en"\s*:\s*\{.*?\n)(\s*\}\s*\})', text, re.DOTALL)

if match:
    tr_part = match.group(1)
    en_part = match.group(2)
    end_part = match.group(3)

    new_tr_str = ",\n" + ",\n".join([f'        "{k}": "{v["tr"]}"' for k,v in NEW_TRANSLATIONS.items()])
    new_en_str = ",\n" + ",\n".join([f'        "{k}": "{v["en"]}"' for k,v in NEW_TRANSLATIONS.items()])

    # Only append if not already there
    if '"audit_no_logs"' not in tr_part:
        # Strip trailing newline and braces for insertion
        new_tr_part = tr_part.rstrip() + new_tr_str + "\n"
        new_en_part = en_part.rstrip() + new_en_str + "\n"

        new_text = text[:match.start()] + new_tr_part + new_en_part + end_part + text[match.end():]
        
        with open('ui/i18n.py', 'w', encoding='utf-8') as f:
            f.write(new_text)
        print("Successfully injected translations into ui/i18n.py!")
else:
    print("Could not match TRANSLATIONS dict")
