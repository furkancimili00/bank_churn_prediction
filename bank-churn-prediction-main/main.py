from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import skops.io as sio
import os
import pandas as pd
from utils import preprocess_data

# 1. FastAPI uygulamasını başlatıyoruz
app = FastAPI(
    title="Banka Churn Tahmin API",
    description="Müşterilerin bankayı terk etme (churn) riskini hesaplayan XAI destekli kurumsal API",
    version="1.0.0"
)

# Güvenlik Ayarları
API_KEY = os.getenv("CHURN_API_KEY")
API_KEY_NAME = "X-API-Key"
api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header_scheme)):
    """
    İstek başlığındaki API anahtarını doğrular.
    Eğer CHURN_API_KEY ortam değişkeni ayarlanmamışsa, güvenlik nedeniyle tüm istekler reddedilir.
    """
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API anahtarı sunucu tarafında yapılandırılmamış.",
        )

    if api_key == API_KEY:
        return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz veya eksik API Anahtarı",
    )

# 2. Kaydettiğimiz modeli ve ön işleme araçlarını hafızaya yüklüyoruz.
# (API her çalıştığında sadece bir kere yüklenir, her istekte tekrar yüklenmez - Performans için kritik)
try:
    model_pack = sio.load('churn_thesis_model.skops')
    model = model_pack['model']
    scaler = model_pack['scaler']
    expected_features = model_pack['features']
except Exception as e:
    print(f"Model yüklenirken hata oluştu: {e}")
    model, scaler, expected_features = None, None, None


# 3. Pydantic ile Veri Doğrulama Şeması (Banka sisteminden gelecek verinin formatı)
# Banka, API'ye bir müşteri verisi gönderdiğinde tam olarak bu değişkenleri ve tipleri göndermek zorundadır.
class CustomerData(BaseModel):
    CreditScore: int
    Geography: str
    Gender: str
    Age: int
    Tenure: int
    Balance: float
    NumOfProducts: int
    HasCrCard: int
    IsActiveMember: int
    EstimatedSalary: float


# 4. Endpoint: Sadece sistemin çalışıp çalışmadığını test etmek için
@app.get("/")
def health_check():
    return {"status": "success", "message": "Churn Tahmin API aktif olarak çalışıyor."}


# 5. Endpoint: Asıl tahmini yapacak olan POST isteği
@app.post("/predict", dependencies=[Depends(get_api_key)])
def predict_churn(customer: CustomerData):
    if model is None:
        raise HTTPException(status_code=500, detail="Makine öğrenmesi modeli yüklenemedi.")

    # Gelen veriyi bir sözlüğe (dictionary), sonra da Pandas DataFrame'e çeviriyoruz
    customer_dict = customer.model_dump()
    df_input = pd.DataFrame([customer_dict])

    # VERİ ÖN İŞLEME
    scaled_input = preprocess_data(df_input, expected_features, scaler)

    # TAHMİN (Prediction)
    # predict_proba ile sadece 0-1 değil, % kaç ihtimalle churn olacağını buluyoruz.
    churn_probability = model.predict_proba(scaled_input)[0][1]
    churn_prediction = int(model.predict(scaled_input)[0])

    # Riske göre kategori belirleme (Bankanın aksiyon alabilmesi için iş kuralı)
    if churn_probability >= 0.70:
        risk_level = "Çok Yüksek Riskli - Acil İletişime Geçilmeli"
    elif churn_probability >= 0.40:
        risk_level = "Orta Riskli - Kampanya Önerilebilir"
    else:
        risk_level = "Düşük Riskli - Sadık Müşteri"

    # Standart ve kurumsal bir JSON dönüşü
    return {
        "churn_tahmini": churn_prediction,
        "churn_ihtimali": round(float(churn_probability), 4),
        "risk_seviyesi": risk_level,
        "mesaj": "Tahmin başarıyla hesaplandı."
    }