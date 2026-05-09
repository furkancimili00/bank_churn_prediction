"""Streamlit ve testler icin geriye uyumlu tahmin yardimcilari."""

from typing import Any, Optional

import numpy as np
import pandas as pd
import shap

from core.config import get_settings
from core.logging_config import get_logger
from services.model_loader import load_model_artifacts
from services.prediction_service import PredictionService

logger = get_logger(__name__)

_MODEL_CACHE: Optional[tuple[Any, Any, list[str]]] = None
_EXPLAINER_CACHE: dict[int, Any] = {}


def load_local_model() -> tuple[Any, Any, Optional[list[str]]]:
    """Yerel model, scaler ve beklenen ozellikleri yukler.

    Returns:
        tuple[Any, Any, Optional[list[str]]]: Model, scaler ve ozellik listesi.
    """
    global _MODEL_CACHE

    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    try:
        artifacts = load_model_artifacts(get_settings().model_path)
        _MODEL_CACHE = (
            artifacts.model,
            artifacts.scaler,
            artifacts.expected_features,
        )
        return _MODEL_CACHE
    except Exception as exc:
        logger.error(f"Model dosyasi yuklenemedi: {exc}")
        return None, None, None


def get_shap_explainer(_model: Any) -> Any:
    """SHAP aciklayicisini model kimligine gore onbellekten dondurur.

    Args:
        _model: Aciklanacak agac tabanli model.

    Returns:
        Any: SHAP TreeExplainer nesnesi.
    """
    cache_key = id(_model)
    if cache_key not in _EXPLAINER_CACHE:
        _EXPLAINER_CACHE[cache_key] = shap.TreeExplainer(_model)

    return _EXPLAINER_CACHE[cache_key]


def make_prediction(
    data_dict: dict[str, Any],
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> dict[str, Any]:
    """Sozluk formatindaki musteri verisinden tekil tahmin uretir.

    Args:
        data_dict: Musteri ozellikleri.
        local_model: Yuklu model nesnesi.
        local_scaler: Yuklu olceklendirici nesne.
        expected_features: Modelin bekledigi ozellik listesi.

    Returns:
        dict[str, Any]: Tahmin, olasilik ve risk seviyesi.
    """
    service = PredictionService(local_model, local_scaler, expected_features)
    return service.predict_one(data_dict)


def make_batch_prediction(
    df_input: pd.DataFrame,
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> np.ndarray:
    """Toplu tahmin icin churn olasiliklarini vektorel olarak uretir.

    Args:
        df_input: Tahmin edilecek musteri verileri.
        local_model: Yuklu model nesnesi.
        local_scaler: Yuklu olceklendirici nesne.
        expected_features: Modelin bekledigi ozellik listesi.

    Returns:
        np.ndarray: Churn olasiliklari.
    """
    service = PredictionService(local_model, local_scaler, expected_features)
    return service.predict_probabilities(df_input)
