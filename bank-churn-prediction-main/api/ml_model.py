"""API katmani icin model bilesenlerini yukleyen uyumluluk modulu."""

from typing import Any, Optional

from core.config import get_settings
from core.logging_config import get_logger
from domain.risk import classify_risk
from services.model_loader import load_model_artifacts

logger = get_logger(__name__)

model: Optional[Any] = None
scaler: Optional[Any] = None
expected_features: Optional[list[str]] = None


def load_api_model() -> tuple[Any, Any, Optional[list[str]]]:
    """API icin model bilesenlerini yukler ve modul seviyesinde saklar.

    Returns:
        tuple[Any, Any, Optional[list[str]]]: Model, scaler ve ozellik listesi.
    """
    global model, scaler, expected_features

    try:
        artifacts = load_model_artifacts(get_settings().model_path)
        model = artifacts.model
        scaler = artifacts.scaler
        expected_features = artifacts.expected_features
        logger.info(
            f"Model basariyla yuklendi. Ozellik sayisi: {len(expected_features)}"
        )
    except Exception as exc:
        logger.error(f"Model yuklenirken hata olustu: {exc}")
        model, scaler, expected_features = None, None, None

    return model, scaler, expected_features


load_api_model()
