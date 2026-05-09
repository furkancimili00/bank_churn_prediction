import sys
import os
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

# Proje ana dizinini Python yoluna ekle ki dashboard modülü içeri aktarılabilsin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# expected_features için bir örnek tanımlayalım
mock_features = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Geography_Germany",
    "Geography_Spain",
    "Gender_Male",
]

# Modeli ve load_local_model'ı patch'liyoruz
with patch("skops.io.load") as mock_load:
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.8, 0.2]])  # Düşük risk

    mock_scaler = MagicMock()
    mock_scaler.transform.side_effect = lambda x: x  # Gelen veriyi aynen döndür

    mock_pack = {"model": mock_model, "scaler": mock_scaler, "features": mock_features}
    mock_load.return_value = mock_pack

    import services.prediction as services_prediction


def test_make_prediction_eksik_ozellikler():
    """
    make_prediction fonksiyonunun, beklenen özelliklerin (expected_features)
    eksik olması durumunda (edge case) bu eksik sütunları 0 değeriyle doldurup
    doldurmadığını test eder.
    """

    # Eksik veri içeren sözlük. Sadece 3 özellik veriyoruz, geri kalanlar eksik.
    # get_dummies sonrası 'Geography' ve 'Gender' için sütunlar (örn: Geography_Germany) çıkmayacak.
    eksik_musteri_verisi = {
        "CreditScore": 650,
        "Age": 40,
        "Balance": 50000.0,
        # Diğer özellikler bilerek dahil edilmemiştir (örn: Tenure, Geography, vb.)
    }

    # Tahmin fonksiyonunu çağırıyoruz
    sonuc = services_prediction.make_prediction(
        eksik_musteri_verisi, mock_model, mock_scaler, mock_features
    )

    # Fonksiyonun hata vermeden çalışıp sonuç döndürdüğünü doğrula
    assert "churn_tahmini" in sonuc
    assert "churn_ihtimali" in sonuc
    assert "risk_seviyesi" in sonuc

    # mock_scaler.transform'a gönderilen DataFrame'i al
    # args[0] fonksiyonun aldığı ilk argüman yani df_input
    cagri_argumanlari = mock_scaler.transform.call_args
    assert cagri_argumanlari is not None, "Scaler transform metodu çağrılmadı"

    df_scaler_input = cagri_argumanlari[0][0]

    # 1. Tüm expected_features sütunlarının oluşturulduğunu kontrol et
    for col in mock_features:
        assert col in df_scaler_input.columns, f"Eksik sütun: {col} df_input içinde yok"

    # 2. Verilen özelliklerin değerlerinin doğru olduğunu kontrol et
    assert df_scaler_input.iloc[0]["CreditScore"] == 650
    assert df_scaler_input.iloc[0]["Age"] == 40
    assert df_scaler_input.iloc[0]["Balance"] == 50000.0

    # 3. Verilmeyen (eksik olan) özelliklerin 0 ile doldurulduğunu kontrol et
    eksik_olan_sutunlar = [
        col for col in mock_features if col not in ["CreditScore", "Age", "Balance"]
    ]
    for col in eksik_olan_sutunlar:
        assert (
            df_scaler_input.iloc[0][col] == 0
        ), f"Sütun {col} 0 değil, değeri: {df_scaler_input.iloc[0][col]}"
