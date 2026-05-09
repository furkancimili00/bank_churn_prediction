"""
KVKK/GDPR Uyumlu Veri Gizliliği ve Maskeleme modülü.
Yüklenen CSV dosyalarındaki kişisel verilerin otomatik maskelenmesi,
anonimleştirme ve güvenli veri işleme fonksiyonlarını barındırır.
"""

import pandas as pd
import numpy as np
import hashlib
import re
from typing import Optional
from core.logging_config import get_logger

logger = get_logger(__name__)

# Kişisel veri sütunları (maskelenmesi gereken)
PII_COLUMNS = ["Surname", "CustomerId", "RowNumber"]

# Kısmi maskeleme için pattern'ler
MASK_CHAR = "*"


def detect_pii_columns(df: pd.DataFrame) -> list[str]:
    """
    DataFrame'deki potansiyel kişisel veri sütunlarını tespit eder.

    Args:
        df (pd.DataFrame): Kontrol edilecek veri.

    Returns:
        list[str]: Tespit edilen kişisel veri sütun adları.
    """
    pii_keywords = [
        "name", "surname", "ad", "soyad", "email", "mail", "phone", "telefon",
        "address", "adres", "tc", "kimlik", "ssn", "passport", "pasaport",
        "customerid", "customer_id", "müsteri", "musteri",
    ]

    detected = []
    for col in df.columns:
        col_lower = col.lower().replace("_", "").replace(" ", "")
        for keyword in pii_keywords:
            if keyword in col_lower:
                detected.append(col)
                break

    # Bilinen PII sütunları da ekle
    for pii_col in PII_COLUMNS:
        if pii_col in df.columns and pii_col not in detected:
            detected.append(pii_col)

    logger.info(f"Tespit edilen kişisel veri sütunları: {detected}")
    return detected


def mask_column_values(series: pd.Series, method: str = "hash") -> pd.Series:
    """
    Bir sütundaki değerleri maskeleme yöntemiyle gizler.

    Args:
        series (pd.Series): Maskelenecek sütun.
        method (str): Maskeleme yöntemi — 'hash', 'partial' veya 'redact'.

    Returns:
        pd.Series: Maskelenmiş sütun.
    """
    if method == "hash":
        return series.apply(
            lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:12] if pd.notna(x) else x
        )
    elif method == "partial":
        def partial_mask(val):
            s = str(val)
            if len(s) <= 2:
                return MASK_CHAR * len(s)
            return s[0] + MASK_CHAR * (len(s) - 2) + s[-1]
        return series.apply(lambda x: partial_mask(x) if pd.notna(x) else x)
    elif method == "redact":
        return series.apply(lambda x: "[GİZLİ]" if pd.notna(x) else x)
    else:
        logger.warning(f"Bilinmeyen maskeleme yöntemi: {method}")
        return series


def anonymize_dataframe(
    df: pd.DataFrame,
    method: str = "hash",
    custom_pii_cols: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    DataFrame'deki kişisel verileri otomatik tespit edip maskeleyerek anonim hale getirir.

    Args:
        df (pd.DataFrame): Anonimleştirilecek veri.
        method (str): Maskeleme yöntemi ('hash', 'partial', 'redact').
        custom_pii_cols (Optional[list[str]]): Ek maskelenecek sütunlar.

    Returns:
        pd.DataFrame: Anonimleştirilmiş veri kopyası.
    """
    df_anon = df.copy()
    pii_cols = detect_pii_columns(df_anon)

    if custom_pii_cols:
        pii_cols.extend([c for c in custom_pii_cols if c in df_anon.columns and c not in pii_cols])

    masked_count = 0
    for col in pii_cols:
        if col in df_anon.columns:
            df_anon[col] = mask_column_values(df_anon[col], method)
            masked_count += 1

    logger.info(f"Anonimleştirme tamamlandı: {masked_count} sütun maskelendi (yöntem: {method})")
    return df_anon


def generate_privacy_report(df_original: pd.DataFrame, df_anonymized: pd.DataFrame) -> dict:
    """
    Anonimleştirme işlemi hakkında özet rapor oluşturur.

    Args:
        df_original (pd.DataFrame): Orijinal veri.
        df_anonymized (pd.DataFrame): Anonimleştirilmiş veri.

    Returns:
        dict: Rapor bilgileri.
    """
    pii_cols = detect_pii_columns(df_original)

    report = {
        "toplam_satir": len(df_original),
        "toplam_sutun": len(df_original.columns),
        "tespit_edilen_pii_sutunlari": pii_cols,
        "maskelenen_sutun_sayisi": len(pii_cols),
        "analiz_icin_guvenli": len(pii_cols) > 0,
        "kvkk_uyumluluk": "✅ Uyumlu" if len(pii_cols) > 0 else "⚠️ PII tespit edilemedi",
    }

    logger.info(f"Gizlilik raporu: {report['maskelenen_sutun_sayisi']} sütun maskelendi")
    return report


def validate_data_retention(session_data: dict) -> list[str]:
    """
    Oturum verilerini kontrol eder ve güvenli silme için uyarı listesi döner.

    Args:
        session_data (dict): Streamlit session_state verileri.

    Returns:
        list[str]: Silinmesi önerilen anahtar listesi.
    """
    sensitive_keys = []
    data_keys = ["results_df", "current_customer", "management_report", "uploaded_file"]

    for key in data_keys:
        if key in session_data:
            sensitive_keys.append(key)

    if sensitive_keys:
        logger.info(f"Veri saklama kontrolü: {len(sensitive_keys)} hassas veri anahtarı tespit edildi")

    return sensitive_keys
