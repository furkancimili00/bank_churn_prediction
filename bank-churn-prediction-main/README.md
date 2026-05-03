# 🏦 Banka Müşteri Kayıp (Churn) Tahmini ve Analiz Paneli

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Modern_API-05998b.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)

Bu proje, bankacılık sektöründeki müşteri terkini (churn) tahmin etmek amacıyla geliştirilen kapsamlı bir makine öğrenmesi tez projesi ve uçtan uca (end-to-end) bir karar destek sistemidir. Sadece tahmin yapmakla kalmaz, tahminin nedenini açıklar ve portföy yöneticileri için çözüm yolları simüle eder.

### 🎓 Akademik Ekip
* **Geliştiriciler:** Enis Çelik, Furkan Çimili, Ahmet Arif Sarı
* **Danışman:** Dr. Öğr. Üy. Gökhan Göksel (Eskişehir Teknik Üniversitesi)

---

## 🚀 Canlı Uygulama
Uygulamayı tarayıcınızda hemen deneyin:
🔗 **[https://bank-churn-prediction-eaf.streamlit.app/]**

> **🔐 Giriş Bilgileri:**
> * **Kullanıcı Adı:** `admin`
> * **Şifre:** `123456` 

---

## ✨ Temel Özellikler

| Özellik | Açıklama |
| :--- | :--- |
| **🔍 Akıllı Tahmin** | XGBoost ve Random Forest algoritmaları ile %86+ doğruluk oranı. |
| **💡 Neden Analizi (SHAP)** | Modelin kararlarını (Yaş, Bakiye, Aktiflik vb.) şeffaf şekilde açıklar. |
| **🧪 What-If Simülatörü** | Müşteriye uygulanacak aksiyonların (Kredi kartı verme vb.) risk üzerindeki etkisini ölçer. |
| **💰 Finansal Etki (CLTV)** | Ayrılma riski durumunda bankanın uğrayacağı **Beklenen Kayıp (€)** tutarını hesaplar. |
| **📂 Toplu Analiz** | CSV dosyası yükleyerek tüm portföyü finansal önceliğe göre sıralar. |

---

## 🛠️ Teknik Mimari ve Teknoloji Yığını (C4 Modeli)
Proje mimarisi aşağıdaki veri ve işlem boru hatlarına (pipeline) göre tasarlanmıştır:
* **Veri İşleme (Data Pipeline):** Pandas, Seaborn ile EDA; OneHotEncoder, StandardScaler ve SMOTE ile veri dengesizliklerinin giderilmesi.
* **Makine Öğrenmesi (ML Server):** Scikit-Learn ve XGBoost (GridSearchCV ile hiperparametre optimizasyonu).
* **API ve Dağıtım:** FastAPI (Dockerized mikroservis mimarisi).
* **Arayüz (UI):** Streamlit (Güvenli giriş ve Secrets Management altyapısı ile).

---

## 🤖 Yapay Zeka (Jules) İçin Geliştirme Öncelikleri ve Başarı Kriterleri
Bu depo üzerinde çalışan otonom ajanların (Jules) geliştirmeleri yaparken şu metrikleri hedeflemesi beklenmektedir:
1. **Model Performansı:** Test veri setinde ROC-AUC değerinin >0.90 ve F1-skorunun >0.85 olarak korunması/iyileştirilmesi.
2. **Performans Süresi:** Web uygulaması üzerinden yapılan tahmin API çağrılarının 1 saniyenin altında (<1s) yanıt vermesi.
3. **Adil Altyapı:** Model tahminlerindeki algoritmik önyargının (bias) azaltılarak etik ve adil bir dağılım sağlanması (bias ratio < 1.2).
4. **Kalite:** Projenin akademik standartlarda modüler olması, PEP8 kodlama standartlarının korunması ve XAI (Açıklanabilir Yapay Zeka) prensiplerinden taviz verilmemesi.

---

## 📦 Kurulum ve Çalıştırma

### 1. Docker ile API Sunucusunu Başlatma
```bash
docker build -t churn-api .
docker run -d -p 8000:8000 churn-api