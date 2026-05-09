"""FastAPI bagimliliklari ve ortak servis saglayicilari."""

import os
import sys
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from api import ml_model
from core.config import get_settings
from core.security import is_valid_api_key
from services.prediction_service import PredictionService

API_KEY = get_settings().api_key
API_KEY_NAME = "X-API-Key"
api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def _get_compatible_main_attr(name: str, fallback: Any) -> Any:
    """Eski test sozlesmesi icin main modulundeki yamalanmis degeri okur.

    Args:
        name: Okunacak alan adi.
        fallback: Alan bulunamazsa kullanilacak deger.

    Returns:
        Any: main modulundeki veya varsayilan deger.
    """
    main_module = sys.modules.get("main")
    if main_module is not None and hasattr(main_module, name):
        return getattr(main_module, name)

    return fallback


def get_configured_api_key() -> Optional[str]:
    """Guncel API anahtarini merkezi ayarlardan veya uyumluluk alanindan okur.

    Returns:
        Optional[str]: Sunucu tarafinda tanimli API anahtari.
    """
    main_module = sys.modules.get("main")
    if main_module is not None and hasattr(main_module, "API_KEY"):
        return getattr(main_module, "API_KEY")

    return os.getenv("CHURN_API_KEY") or API_KEY


async def get_api_key(
    api_key: Optional[str] = Depends(api_key_header_scheme),
) -> str:
    """Istek basligindaki API anahtarini dogrular.

    Args:
        api_key: X-API-Key basligindan gelen anahtar.

    Returns:
        str: Dogrulanmis API anahtari.

    Raises:
        HTTPException: Anahtar eksik, gecersiz veya yapilandirilmamis ise.
    """
    configured_api_key = get_configured_api_key()
    env_api_key = os.getenv("CHURN_API_KEY")
    if not configured_api_key and env_api_key and api_key in (None, env_api_key):
        configured_api_key = env_api_key

    if not configured_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API anahtarı sunucu tarafında yapılandırılmamış.",
        )

    if is_valid_api_key(api_key, configured_api_key):
        return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz veya eksik API Anahtarı",
    )


def get_prediction_service() -> PredictionService:
    """Tahmin servisini calisma zamani model bilesenleriyle olusturur.

    Returns:
        PredictionService: Route katmaninin kullanacagi tahmin servisi.
    """
    model = _get_compatible_main_attr("model", ml_model.model)
    scaler = _get_compatible_main_attr("scaler", ml_model.scaler)
    expected_features = _get_compatible_main_attr(
        "expected_features",
        ml_model.expected_features,
    )
    return PredictionService(model, scaler, expected_features)
