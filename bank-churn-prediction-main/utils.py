import pandas as pd
import numpy as np

def preprocess_data(df_input: pd.DataFrame, expected_features: list, scaler) -> np.ndarray:
    """
    Verilen DataFrame'i modelin beklediği formata getirir.
    One-Hot Encoding, sütun hizalama ve ölçeklendirme işlemlerini yapar.

    Args:
        df_input: İşlenecek veri (Pandas DataFrame formatında)
        expected_features: Modelin eğitiminde kullanılan özelliklerin listesi
        scaler: Ölçeklendirme (StandardScaler vs.) objesi

    Returns:
        İşlenmiş ve ölçeklendirilmiş veri
    """
    if scaler is None:
        raise ValueError("Scaler objesi None olamaz. Lütfen 'scaler.skops' dosyasının doğru yüklendiğinden emin olun.")

    if not expected_features:
        raise ValueError("Beklenen özellikler (expected_features) boş veya None olamaz.")

    # Kategorik verileri sayısal formata çeviriyoruz (One-Hot Encoding)
    df_encoded = pd.get_dummies(df_input, drop_first=True)

    # Eksik sütunları (expected_features) 0 ile dolduruyoruz
    df_aligned = df_encoded.reindex(columns=expected_features, fill_value=0)

    # Scaling
    scaled_input = scaler.transform(df_aligned)

    return scaled_input
