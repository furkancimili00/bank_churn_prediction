import pandas as pd
import numpy as np
import shap
import skops.io as sio
import asyncio
import streamlit as st
from utils import preprocess_data


@st.cache_resource
def load_local_model():
    """
    Diskteki model, scaler ve beklenen özellikleri yükler.

    Returns:
        tuple: (model, scaler, expected_features)
    """
    try:
        pack = sio.load("churn_thesis_model.skops", trusted=True)
        return pack["model"], pack["scaler"], pack["features"]
    except Exception as e:
        st.error(f"Model dosyası yüklenemedi: {e}")
        return None, None, None


@st.cache_resource
def get_shap_explainer(_model):
    """
    SHAP model açıklayıcısını önbelleğe alır (caching).
    TreeExplainer hesaplaması maliyetli olduğundan her render işleminde baştan hesaplanmasını engeller.

    Args:
        _model: Açıklanacak XGBoost/Tree tabanlı model.

    Returns:
        shap.TreeExplainer: Model açıklayıcısı
    """
    asyncio.set_event_loop(asyncio.new_event_loop())
    return shap.TreeExplainer(_model)


def make_prediction(
    data_dict: dict, local_model, local_scaler, expected_features
) -> dict:
    """
    Gelen sözlük (dict) formatındaki veriden tekil bir tahmin (prediction) üretir.

    Args:
        data_dict (dict): Müşteri özellikleri.
        local_model: Yüklü model objesi.
        local_scaler: Yüklü ölçeklendirme objesi.
        expected_features: Beklenen sütun adları listesi.

    Returns:
        dict: churn tahmini (0 veya 1), churn ihtimali (float) ve risk seviyesini içeren sözlük.
    """
    df_input = pd.DataFrame([data_dict])

    # Yeni Utils Fonksiyonu ile Ön İşleme
    scaled_input = preprocess_data(df_input, expected_features, local_scaler)

    # Tahmin
    prob = local_model.predict_proba(scaled_input)[0][1]
    pred = int(prob > 0.5)

    return {
        "churn_tahmini": pred,
        "churn_ihtimali": float(prob),
        "risk_seviyesi": "Yüksek" if prob > 0.7 else "Orta" if prob > 0.4 else "Düşük",
    }


def make_batch_prediction(
    df_input: pd.DataFrame, local_model, local_scaler, expected_features
) -> np.ndarray:
    """
    Toplu tahmin için optimize edilmiş tahmin fonksiyonu.

    Args:
        df_input (pd.DataFrame): Tahmin edilecek müşteri verilerini içeren DataFrame.
        local_model: Yüklü model objesi.
        local_scaler: Yüklü ölçeklendirme objesi.
        expected_features: Beklenen sütun adları listesi.

    Returns:
        np.ndarray: Tahmin olasılıklarını içeren dizi.
    """
    # Yeni Utils Fonksiyonu ile Ön İşleme
    scaled_input = preprocess_data(df_input, expected_features, local_scaler)

    # Tahmin
    probs = local_model.predict_proba(scaled_input)[:, 1]

    return probs
