# THESIS_CONTEXT.md: Bank Customer Churn Prediction

Bu belge, "Bank Customer Churn Prediction Using Machine Learning Techniques" başlıklı bitirme tezinin otonom kalite güvence (QA) süreçleri için temel anayasayı oluşturur[cite: 1]. Sisteme entegre edilen tüm yapay zeka ajanları (özellikle QA Ajanı), projeyi geliştirirken ve test ederken bu belgedeki metrikleri ve sınırları referans almak zorundadır[cite: 1].

## 1. Başarı Metrikleri (Success Metrics)
*   **Model Performansı (Dengesiz Veri):** Sınıf dengesizlikleri (SMOTE vb. ile) giderildikten sonra F1-skorunun 0.85'in üzerinde olması hedeflenmektedir[cite: 1].
*   **Genel Eğitim Başarısı:** Modellerin (Lojistik Regresyon, Random Forest, XGBoost) ROC-AUC değerinin 0.90'ın üzerinde olması gerekmektedir[cite: 1].
*   **Adillik ve Etik (Fairness):** SHAP (Explainable AI) entegrasyonu ile model yanlılığının (bias) %15'e kadar azaltılması ve "disparate impact" oranının 1.2'nin altında tutulması şarttır[cite: 1].
*   **Uygulama Performansı:** Geliştirilen Flask veya Streamlit tabanlı web API'sinin yanıt süresi 1 saniyenin altında olmalıdır[cite: 1].
*   **Kıyaslama İyileştirmesi:** XGBoost gibi topluluk (ensemble) algoritmalarının, veri dengesizliğini yönetmede temel sınıflandırıcılara göre F1-skorunda en az %10'luk bir iyileşme sağlaması beklenmektedir[cite: 1].

## 2. Akademik Hedefler (Academic Goals)
*   **Akademik Yayın:** Nisan 2026'ya kadar IEEE Sinyal İşleme ve İletişim Uygulamaları Kurultayı'na (SIU 2026) 1 adet konferans bildirisi sunulması planlanmaktadır[cite: 1].
*   **Tez Raporu:** Gelecekteki makine öğrenmesi çalışmaları için referans niteliğinde, 35-40 sayfalık kapsamlı bir tez raporu hazırlanacaktır[cite: 1].
*   **Açık Kaynak Katkısı:** Projenin GitHub deposunun 6 ay içinde 100'den fazla yıldıza (star) ulaşması hedeflenmektedir[cite: 1].
*   **Sürdürülebilirlik:** Proje çıktılarının, Birleşmiş Milletler Sürdürülebilir Kalkınma Amaçları'ndan (SDG) 4 (Nitelikli Eğitim), 8 (İnsana Yakışır İş ve Büyüme), 9 (Sanayi, Yenilikçilik ve Altyapı), 10 (Eşitsizliklerin Azaltılması) ve 12 (Sorumlu Üretim) numaralı hedeflerle uyumlu olması gerekmektedir[cite: 1].

## 3. Teknik Sınırlar ve Kısıtlamalar (Technical Constraints)
*   **Veri Seti Parametreleri:** Kaggle üzerinden sağlanan, yaş, hesap bakiyesi, müşteri terk durumu gibi özellikler barındıran, 10.000 satır ve 14 öznitelikli veri setleri kullanılacaktır[cite: 1].
*   **Teknoloji Yığını:** Sistem Python 3.9+ ortamında geliştirilecek; veri işleme ve modelleme için Pandas, Numpy, Scikit-learn, XGBoost, SHAP; web ve dağıtım için Flask, Streamlit ve Docker kullanılacaktır[cite: 1].
*   **Zaman Çizelgesi:** Çalışmalar Kasım 2025'te veri analiziyle (EDA) başlayıp, Nisan 2026'da değerlendirme süreciyle sona erecek şekilde 6 aylık katı bir takvime bağlıdır[cite: 1].
*   **Yasal ve Güvenlik Sınırları:** Platform, KVKK ve GDPR regülasyonlarına uygun olacak şekilde veri anonimleştirme tekniklerini barındırmalıdır[cite: 1].
*   **Altyapı Kısıtlamaları:** Geliştirme süreci kişisel bilgisayarlarda, Eskişehir Teknik Üniversitesi laboratuvarlarındaki iş istasyonlarında ve bulut platformlarında (Google Colab) düşük maliyetli kaynaklarla yürütülecektir[cite: 1].