"""Tahmin endpoint'lerini tanimlayan API router modulu."""

from fastapi import APIRouter, Depends, HTTPException, Request

from api.dependencies import get_api_key, get_prediction_service
from api.limiter import limiter
from api.schemas import BatchCustomerData, CustomerData
from core.config import get_settings
from core.logging_config import get_logger
from services.audit_service import log_event
from services.prediction_service import PredictionService

logger = get_logger(__name__)

router = APIRouter(
    dependencies=[Depends(get_api_key)],
    tags=["Tahmin Servisleri"],
)


@router.get("/model-info")
def model_info(
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> dict:
    """Yuklu modelin metadata bilgilerini dondurur.

    Args:
        prediction_service: Calisma zamani model bilesenlerini tasiyan servis.

    Returns:
        dict: Model versiyonu, tipi, ozellikleri ve risk esikleri.
    """
    if not prediction_service.is_ready():
        raise HTTPException(status_code=500, detail="Model yüklenmemiş.")

    return {
        "api_version": get_settings().api_version,
        "model_type": type(prediction_service.model).__name__,
        "feature_count": len(prediction_service.expected_features),
        "features": prediction_service.expected_features,
        "risk_thresholds": {
            "yuksek": ">= 0.70",
            "orta": ">= 0.40",
            "dusuk": "< 0.40",
        },
        "status": "aktif",
    }


@router.post("/predict")
@limiter.limit("10/minute")
def predict_churn(
    request: Request,
    customer: CustomerData,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> dict:
    """Tekil musteri verisi alarak churn tahminini hesaplar.

    Args:
        request: Rate limit icin FastAPI istek nesnesi.
        customer: Dogrulanmis musteri verisi.
        prediction_service: Churn tahmin is mantigini yurutur.

    Returns:
        dict: Tekil tahmin sonucu.
    """
    if not prediction_service.is_ready():
        raise HTTPException(
            status_code=500,
            detail="Makine öğrenmesi modeli yüklenemedi.",
        )

    result = prediction_service.predict_one(customer.model_dump())
    result["churn_ihtimali"] = round(float(result["churn_ihtimali"]), 4)
    result["mesaj"] = "Tahmin başarıyla hesaplandı."

    return result


@router.post("/batch-predict")
@limiter.limit("5/minute")
def batch_predict_churn(
    request: Request,
    batch: BatchCustomerData,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> dict:
    """Toplu musteri verisi alarak churn tahmini uretir.

    Args:
        request: Rate limit icin FastAPI istek nesnesi.
        batch: Dogrulanmis musteri listesi.
        prediction_service: Churn tahmin is mantigini yurutur.

    Returns:
        dict: Toplu tahmin sonucu ve ozet istatistikler.
    """
    if not prediction_service.is_ready():
        raise HTTPException(
            status_code=500,
            detail="Makine öğrenmesi modeli yüklenemedi.",
        )

    customers = batch.customers
    if len(customers) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Tek seferde en fazla 1000 müşteri işlenebilir.",
        )

    if not customers:
        raise HTTPException(status_code=400, detail="Müşteri listesi boş.")

    result = prediction_service.predict_batch(
        [customer.model_dump() for customer in customers]
    )
    total = result["toplam_musteri"]
    high_risk = result["ozet"]["yuksek_riskli"]

    logger.info(f"Toplu tahmin: {total} musteri, {high_risk} yuksek riskli")
    try:
        log_event(
            "batch_predict",
            {"musteri_sayisi": total, "yuksek_riskli": high_risk},
        )
    except Exception as exc:
        logger.warning(f"Denetim kaydi yazilamadi: {exc}")

    result["mesaj"] = f"{total} müşteri için tahmin başarıyla hesaplandı."

    return result
