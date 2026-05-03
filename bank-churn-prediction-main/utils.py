import pandas as pd
from typing import Any, List

def preprocess_data(data_dict: dict, expected_features: List[str], scaler: Any) -> Any:
    """
    Gelen müşteri verisini modelin beklediği formata dönüştürür.

    Args:
        data_dict (dict): Tekil bir müşteri verisini içeren sözlük.
        expected_features (List[str]): Modelin eğitiminde kullanılan ve beklenen özelliklerin listesi.
        scaler (Any): Veriyi ölçeklendirmek için kullanılan önceden eğitilmiş bir scaler nesnesi (örn. StandardScaler).

    Returns:
        Any: Model tahminine hazır olan ölçeklendirilmiş veri.
    """
    # Gelen veriyi Pandas DataFrame'e çeviriyoruz
    df_input = pd.DataFrame([data_dict])

    # Kategori verilerini One-Hot Encoding'e dönüştürme
    df_input = pd.get_dummies(df_input, drop_first=True)

    # Modelin eğitiminde kullanılan sütun yapısı ile gelen verinin yapısını eşliyoruz.
    # Eksik dummy sütunlar varsa 0 olarak eklenir, fazla olanlar silinir.
    df_input = df_input.reindex(columns=expected_features, fill_value=0)

    # Scaler ile sayısal verileri aynı eğitimdeki gibi ölçeklendiriyoruz
    scaled_input = scaler.transform(df_input)

    return scaled_input
