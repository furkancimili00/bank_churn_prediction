from typing import Any, Optional

import numpy as np
import pandas as pd
import streamlit as st

from services.prediction import make_batch_prediction

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
MAX_BATCH_ROWS = 10000

REQUIRED_COLUMNS = {
    "CreditScore": "int64",
    "Geography": "object",
    "Gender": "object",
    "Age": "int64",
    "Tenure": "int64",
    "Balance": "float64",
    "NumOfProducts": "int64",
    "HasCrCard": "int64",
    "IsActiveMember": "int64",
    "EstimatedSalary": "float64",
}
NUMERIC_COLUMNS = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
]


def _validate_file_size(uploaded_file: Any) -> bool:
    """Yüklenen dosyanın boyut sınırını kontrol eder.

    Args:
        uploaded_file: Streamlit dosya yükleme nesnesi.

    Returns:
        bool: Dosya boyutu uygunsa True.
    """
    if uploaded_file.size <= MAX_FILE_SIZE_BYTES:
        return True

    st.error("❌ Yüklenen dosya boyutu çok büyük! Maksimum 5MB yükleyebilirsiniz.")
    return False


def _read_uploaded_dataframe(uploaded_file: Any) -> Optional[pd.DataFrame]:
    """Yüklenen CSV dosyasını DataFrame olarak okur.

    Args:
        uploaded_file: Streamlit dosya yükleme nesnesi.

    Returns:
        Optional[pd.DataFrame]: Okunan veri veya hata durumunda None.
    """
    try:
        return pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"❌ Dosya okunurken bir hata oluştu: {exc}")
        return None


def _validate_required_columns(df: pd.DataFrame) -> bool:
    """Toplu analiz için zorunlu sütunların varlığını kontrol eder.

    Args:
        df: Yüklenen müşteri verisi.

    Returns:
        bool: Zorunlu sütunlar mevcutsa True.
    """
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if not missing_columns:
        return True

    st.error(f"❌ Yüklenen dosyada eksik sütunlar var: {', '.join(missing_columns)}")
    return False


def _validate_dataframe_shape(df: pd.DataFrame) -> bool:
    """Yüklenen veri boyutunun analiz için uygunluğunu kontrol eder.

    Args:
        df: Yüklenen müşteri verisi.

    Returns:
        bool: Veri boyutu uygunsa True.
    """
    if df.empty:
        st.error("❌ Yüklenen dosya boş.")
        return False

    if len(df) > MAX_BATCH_ROWS:
        st.error(
            "❌ Dosya çok fazla satır içeriyor. "
            "Lütfen en fazla 10.000 satırlık bir dosya yükleyin."
        )
        return False

    return True


def _coerce_numeric_columns(df: pd.DataFrame) -> bool:
    """Sayısal olması gereken sütunları sayısal tipe dönüştürür.

    Args:
        df: Yüklenen müşteri verisi.

    Returns:
        bool: Tüm dönüşümler başarılıysa True.
    """
    try:
        for column in NUMERIC_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="raise")
        return True
    except ValueError as exc:
        st.error(
            "❌ Veri tipi hatası: Dosyadaki veriler beklenilen sayısal formatta değil. "
            f"Detay: {exc}"
        )
        return False


def _validate_uploaded_dataframe(df: pd.DataFrame) -> bool:
    """Yüklenen DataFrame'i toplu analiz öncesinde doğrular.

    Args:
        df: Yüklenen müşteri verisi.

    Returns:
        bool: Veri analiz için uygunsa True.
    """
    return (
        _validate_required_columns(df)
        and _validate_dataframe_shape(df)
        and _coerce_numeric_columns(df)
    )


def _classify_probability(probability: float) -> str:
    """Churn olasılığını kısa risk etiketine dönüştürür.

    Args:
        probability: Churn olasılığı.

    Returns:
        str: Yüksek, Orta veya Düşük risk etiketi.
    """
    if probability > 0.7:
        return "Yüksek"
    if probability > 0.4:
        return "Orta"
    return "Düşük"


def _build_results_dataframe(df: pd.DataFrame, probabilities: np.ndarray) -> pd.DataFrame:
    """Toplu tahmin sonuç DataFrame'ini oluşturur.

    Args:
        df: Analiz edilen müşteri verisi.
        probabilities: Modelin ürettiği churn olasılıkları.

    Returns:
        pd.DataFrame: CLTV öncelikli analiz sonucu.
    """
    customer_values = df["Balance"] + (df["EstimatedSalary"] * 0.20)
    expected_losses = customer_values * probabilities
    customer_ids = df["CustomerId"] if "CustomerId" in df.columns else df.index

    results_df = pd.DataFrame(
        {
            "Müşteri ID": customer_ids,
            "Risk (%)": np.round(probabilities * 100, 2),
            "Risk Seviyesi": [_classify_probability(prob) for prob in probabilities],
            "Müşteri Değeri (€)": np.round(customer_values, 2),
            "Beklenen Kayıp (€)": np.round(expected_losses, 2),
        }
    )
    return results_df.sort_values(by="Beklenen Kayıp (€)", ascending=False).reset_index(
        drop=True
    )


def _run_batch_prediction(
    df: pd.DataFrame,
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> pd.DataFrame:
    """Toplu tahminleri çalıştırır ve sonuç tablosunu üretir.

    Args:
        df: Analiz edilecek müşteri verisi.
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.

    Returns:
        pd.DataFrame: Toplu analiz sonucu.
    """
    df_input = df[list(REQUIRED_COLUMNS.keys())].copy()
    probabilities = make_batch_prediction(
        df_input,
        local_model,
        local_scaler,
        expected_features,
    )
    return _build_results_dataframe(df, probabilities)


def _render_batch_summary(results_df: pd.DataFrame) -> None:
    """Toplu analiz özet metriklerini render eder.

    Args:
        results_df: Toplu analiz sonucu.
    """
    st.write("---")
    st.subheader("📊 Analiz Özeti")

    total_loss = results_df["Beklenen Kayıp (€)"].sum()
    high_risk_count = len(results_df[results_df["Risk Seviyesi"] == "Yüksek"])

    summary_col1, summary_col2 = st.columns(2)
    summary_col1.metric(
        label="Toplam Beklenen Finansal Kayıp",
        value=f"€{total_loss:,.2f}",
    )
    summary_col2.metric(label="Yüksek Riskli Müşteri Sayısı", value=str(high_risk_count))


def _risk_color_style(value: Any) -> str:
    """Risk etiketi için tablo rengi döndürür.

    Args:
        value: Tablo hücresi değeri.

    Returns:
        str: Pandas Styler CSS değeri.
    """
    text_value = str(value)
    if "Yüksek" in text_value:
        return "color: red"
    if "Orta" in text_value:
        return "color: orange"
    return "color: green"


def _render_results_table(results_df: pd.DataFrame) -> None:
    """Toplu analiz detay tablosunu ve indirme butonunu render eder.

    Args:
        results_df: Toplu analiz sonucu.
    """
    st.write("---")
    st.subheader("📋 Detaylı Müşteri Listesi (CLTV Öncelikli)")

    styled_df = results_df.style.map(
        _risk_color_style, subset=["Risk Seviyesi"]
    ).format(
        {
            "Müşteri Değeri (€)": "{:,.2f}",
            "Beklenen Kayıp (€)": "{:,.2f}",
        }
    )

    st.dataframe(styled_df, use_container_width=True)
    csv = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Analiz Raporunu İndir",
        data=csv,
        file_name="toplu_churn_analiz_raporu.csv",
        mime="text/csv",
    )


def _render_batch_results(
    df: pd.DataFrame,
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> None:
    """Toplu analiz çalıştırma butonu ve sonuçlarını render eder.

    Args:
        df: Analiz edilecek müşteri verisi.
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.
    """
    if not st.button("🚀 Tüm Listeyi Analiz Et", use_container_width=True, type="primary"):
        return

    with st.spinner("Toplu analiz yapılıyor... Lütfen bekleyin."):
        progress_bar = st.progress(0)
        results_df = _run_batch_prediction(df, local_model, local_scaler, expected_features)
        progress_bar.progress(1.0)
        st.session_state.results_df = results_df

    _render_batch_summary(results_df)
    _render_results_table(results_df)


def _handle_uploaded_file(
    uploaded_file: Any,
    local_model: Any,
    local_scaler: Any,
    expected_features: list[str],
) -> None:
    """Yüklenen CSV dosyasını doğrular ve toplu analiz akışını başlatır.

    Args:
        uploaded_file: Streamlit dosya yükleme nesnesi.
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.
    """
    if not _validate_file_size(uploaded_file):
        return

    df = _read_uploaded_dataframe(uploaded_file)
    if df is None or not _validate_uploaded_dataframe(df):
        return

    st.success(f"✅ Dosya başarıyla yüklendi. Toplam {len(df)} müşteri kaydı bulundu.")
    _render_batch_results(df, local_model, local_scaler, expected_features)


def render_tab_batch_analysis(
    local_model: Any = None,
    local_scaler: Any = None,
    expected_features: list[str] = None,
) -> None:
    """Toplu müşteri analiz sekmesini render eder.

    Args:
        local_model: Yüklü model nesnesi.
        local_scaler: Yüklü ölçekleyici nesne.
        expected_features: Modelin beklediği özellik listesi.
    """
    st.subheader("📁 Toplu Müşteri Analizi ve Önceliklendirme")
    st.write(
        "Müşteri verilerinizi içeren CSV dosyasını yükleyerek toplu risk analizi "
        "yapabilir ve beklenen finansal kayba göre önceliklendirme alabilirsiniz."
    )

    uploaded_file = st.file_uploader("CSV Dosyası Seçin", type=["csv"])
    if uploaded_file is not None:
        _handle_uploaded_file(uploaded_file, local_model, local_scaler, expected_features)
