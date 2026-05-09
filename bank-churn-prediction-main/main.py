from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import skops.io as sio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import pandas as pd
from core.utils import preprocess_data
from core.logging_config import get_logger

logger = get_logger(__name__)

# ==========================================
# 1. FastAPI Uygulaması
# ==========================================
app = FastAPI(
    title="Banka Churn Tahmin API",
    description="Müşterilerin bankayı terk etme (churn) riskini hesaplayan XAI destekli kurumsal API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware — Üretim ortamı için origin kontrolü
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter Kurulumu
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


# ==========================================
# 2. Model Yükleme
# ==========================================
try:
    untrusted = sio.get_untrusted_types(file="churn_thesis_model.skops")
    model_pack = sio.load("churn_thesis_model.skops", trusted=untrusted)
    model = model_pack["model"]
    scaler = model_pack["scaler"]
    expected_features = model_pack["features"]
    logger.info(f"Model başarıyla yüklendi. Özellik sayısı: {len(expected_features)}")
except Exception as e:
    logger.error(f"Model yüklenirken hata oluştu: {e}")
    model, scaler, expected_features = None, None, None


# ==========================================
# 3. Pydantic Şemaları
# ==========================================
class CustomerData(BaseModel):
    """Tekil müşteri verisi şeması."""
    CreditScore: int = Field(..., ge=300, le=850, description="Müşterinin kredi notu (300-850)")
    Geography: str = Field(..., description="Müşterinin bulunduğu ülke (örn: France, Germany, Spain)")
    Gender: str = Field(..., description="Müşterinin cinsiyeti (Male, Female)")
    Age: int = Field(..., ge=18, le=100, description="Müşterinin yaşı (18-100)")
    Tenure: int = Field(..., ge=0, le=20, description="Müşterinin bankayla çalışma süresi (yıl)")
    Balance: float = Field(..., ge=0.0, description="Hesap bakiyesi")
    NumOfProducts: int = Field(..., ge=1, le=10, description="Kullandığı ürün sayısı")
    HasCrCard: int = Field(..., ge=0, le=1, description="Kredi kartı var mı? (1: Evet, 0: Hayır)")
    IsActiveMember: int = Field(..., ge=0, le=1, description="Aktif üye mi? (1: Evet, 0: Hayır)")
    EstimatedSalary: float = Field(..., ge=0.0, description="Tahmini yıllık maaşı")


class BatchCustomerData(BaseModel):
    """Toplu müşteri verisi şeması."""
    customers: list[CustomerData]


def _classify_risk(probability: float) -> str:
    """
    Churn olasılığına göre risk seviyesi belirler.

    Args:
        probability (float): Churn olasılığı (0.0-1.0).

    Returns:
        str: Risk seviyesi metni.
    """
    if probability >= 0.70:
        return "Çok Yüksek Riskli - Acil İletişime Geçilmeli"
    elif probability >= 0.40:
        return "Orta Riskli - Kampanya Önerilebilir"
    return "Düşük Riskli - Sadık Müşteri"


# ==========================================
# 4. Endpoint'ler
# ==========================================

@app.get("/")
def health_check():
    """
    API'nin çalışıp çalışmadığını kontrol eden sağlık (health-check) bitiş noktası.
    """
    return {"status": "success", "message": "Churn Tahmin API aktif olarak çalışıyor."}


@app.get("/model-info", dependencies=[Depends(get_api_key)])
def model_info():
    """
    Yüklü modelin metadata bilgilerini döner.
    Versiyon, özellik listesi ve model tipi bilgilerini içerir.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model yüklenmemiş.")

    return {
        "api_version": "2.0.0",
        "model_type": type(model).__name__,
        "feature_count": len(expected_features) if expected_features else 0,
        "features": expected_features if expected_features else [],
        "risk_thresholds": {
            "yuksek": ">= 0.70",
            "orta": ">= 0.40",
            "dusuk": "< 0.40",
        },
        "status": "aktif",
    }


@app.post("/predict", dependencies=[Depends(get_api_key)])
@limiter.limit("10/minute")
def predict_churn(request: Request, customer: CustomerData):
    """
    Tekil müşteri verisi alarak churn (terk) tahminini hesaplayan bitiş noktası.

    Args:
        request (Request): Gelen HTTP isteği.
        customer (CustomerData): Tahmin edilecek müşteri verisi.

    Returns:
        dict: Tahmin sonucu, olasılığı ve risk seviyesini içeren sözlük.
    """
    if model is None:
        raise HTTPException(
            status_code=500, detail="Makine öğrenmesi modeli yüklenemedi."
        )

    customer_dict = customer.model_dump()
    df_input = pd.DataFrame([customer_dict])
    scaled_input = preprocess_data(df_input, expected_features, scaler)

    churn_probability = model.predict_proba(scaled_input)[0][1]
    churn_prediction = int(model.predict(scaled_input)[0])
    risk_level = _classify_risk(churn_probability)

    return {
        "churn_tahmini": churn_prediction,
        "churn_ihtimali": round(float(churn_probability), 4),
        "risk_seviyesi": risk_level,
        "mesaj": "Tahmin başarıyla hesaplandı.",
    }


@app.post("/batch-predict", dependencies=[Depends(get_api_key)])
@limiter.limit("5/minute")
def batch_predict_churn(request: Request, batch: BatchCustomerData):
    """
    Toplu müşteri verisi alarak birden fazla müşteri için churn tahmini yapan bitiş noktası.
    Tek seferde en fazla 1000 müşteri işlenebilir.

    Args:
        request (Request): Gelen HTTP isteği.
        batch (BatchCustomerData): Tahmin edilecek müşteri listesi.

    Returns:
        dict: Toplu tahmin sonuçları, özet istatistikler ve her müşteri için detaylı sonuçlar.
    """
    if model is None:
        raise HTTPException(
            status_code=500, detail="Makine öğrenmesi modeli yüklenemedi."
        )

    customers = batch.customers
    if len(customers) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Tek seferde en fazla 1000 müşteri işlenebilir.",
        )

    if not customers:
        raise HTTPException(status_code=400, detail="Müşteri listesi boş.")

    results = []
    all_dicts = [c.model_dump() for c in customers]
    df_all = pd.DataFrame(all_dicts)
    scaled_all = preprocess_data(df_all, expected_features, scaler)

    probas = model.predict_proba(scaled_all)[:, 1]
    preds = model.predict(scaled_all)

    for idx, (prob, pred) in enumerate(zip(probas, preds)):
        results.append({
            "index": idx,
            "churn_tahmini": int(pred),
            "churn_ihtimali": round(float(prob), 4),
            "risk_seviyesi": _classify_risk(prob),
        })

    # Özet istatistikler
    total = len(results)
    high_risk = sum(1 for r in results if r["churn_ihtimali"] >= 0.70)
    medium_risk = sum(1 for r in results if 0.40 <= r["churn_ihtimali"] < 0.70)
    low_risk = total - high_risk - medium_risk
    avg_risk = sum(r["churn_ihtimali"] for r in results) / total if total > 0 else 0

    logger.info(f"Toplu tahmin: {total} müşteri, {high_risk} yüksek riskli")

    # Denetim kaydı
    try:
        from services.audit_service import log_event
        log_event("batch_predict", {"musteri_sayisi": total, "yuksek_riskli": high_risk})
    except Exception:
        pass

    return {
        "toplam_musteri": total,
        "ozet": {
            "yuksek_riskli": high_risk,
            "orta_riskli": medium_risk,
            "dusuk_riskli": low_risk,
            "ortalama_risk": round(avg_risk, 4),
        },
        "sonuclar": results,
        "mesaj": f"{total} müşteri için tahmin başarıyla hesaplandı.",
    }


@app.get("/audit/logs", dependencies=[Depends(get_api_key)])
def get_audit_logs(limit: int = 50):
    """
    Son denetim günlüğü kayıtlarını döner.

    Args:
        limit (int): Döndürülecek maksimum kayıt sayısı (varsayılan: 50).

    Returns:
        dict: Denetim logları ve özet istatistikler.
    """
    from services.audit_service import get_recent_events, get_event_summary

    events = get_recent_events(limit=limit)
    summary = get_event_summary()

    return {
        "ozet": summary,
        "kayitlar": events,
    }

