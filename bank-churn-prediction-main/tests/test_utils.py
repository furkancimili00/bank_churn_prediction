import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

# Proje ana dizinini Python yoluna ekle ki utils modülü içeri aktarılabilsin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import preprocess_data

def test_preprocess_data():
    """
    preprocess_data fonksiyonunun one-hot encoding, sütun hizalama ve
    ölçeklendirme işlemlerini doğru yapıp yapmadığını test eder.
    """
    # Test verisi
    data = {
        "CreditScore": [600],
        "Geography": pd.Categorical(["France"], categories=["France", "Germany", "Spain"]),
        "Gender": pd.Categorical(["Male"], categories=["Female", "Male"]),
        "Age": [40],
        "Tenure": [3],
        "Balance": [60000.0],
        "NumOfProducts": [2],
        "HasCrCard": [1],
        "IsActiveMember": [1],
        "EstimatedSalary": [50000.0]
    }
    df_input = pd.DataFrame(data)

    # Beklenen özellikler listesi
    expected_features = [
        'CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts',
        'HasCrCard', 'IsActiveMember', 'EstimatedSalary',
        'Geography_Germany', 'Geography_Spain', 'Gender_Male'
    ]

    # Dummy scaler
    mock_scaler = MagicMock()
    # Gelen DataFrame'in değerlerini numpy array olarak döndüren dummy transform fonksiyonu
    mock_scaler.transform.side_effect = lambda x: x.to_numpy()

    # Fonksiyonu çalıştır
    result = preprocess_data(df_input, expected_features, mock_scaler)

    # 1. Transform metodunun çağrıldığını doğrula
    mock_scaler.transform.assert_called_once()

    # Transform'a gönderilen argümanı (DataFrame'i) al
    called_df = mock_scaler.transform.call_args[0][0]

    # 2. Sütunların tam olarak expected_features ile aynı olduğunu doğrula
    assert list(called_df.columns) == expected_features

    # 3. One-hot encoding ve reindex değerlerinin doğruluğunu kontrol et
    # "Geography_France" dummy'si get_dummies(drop_first=True) ile silinmiş olmalı ve listede yok
    # "Geography_Germany" ve "Geography_Spain" 0 ile doldurulmuş olmalı
    assert called_df.iloc[0]["Geography_Germany"] == 0
    assert called_df.iloc[0]["Geography_Spain"] == 0
    # "Gender_Male" 1 olmalı
    assert called_df.iloc[0]["Gender_Male"] == 1

    # Sayısal değerler aynen korunmuş olmalı
    assert called_df.iloc[0]["CreditScore"] == 600
    assert called_df.iloc[0]["Age"] == 40

    # 4. Sonuç tipinin dummy scaler tarafından döndürülen tip (numpy array) olduğunu doğrula
    assert isinstance(result, np.ndarray)
