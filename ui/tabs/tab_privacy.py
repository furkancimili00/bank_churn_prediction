import streamlit as st
import pandas as pd
from services.data_privacy import (
    anonymize_dataframe,
    detect_pii_columns,
    generate_privacy_report,
)

def render_tab_privacy(local_model=None, local_scaler=None, expected_features=None):
        st.subheader("🔒 Veri Gizliliği ve Anonimleştirme (KVKK/GDPR)")
        st.write(
            "CSV dosyanızdaki kişisel verileri (ad, soyad, müşteri ID) otomatik tespit edip "
            "maskeleyerek KVKK/GDPR uyumlu hale getirin."
        )
    
        privacy_file = st.file_uploader(
            "Anonimleştirilecek CSV Dosyası Yükleyin", type=["csv"], key="privacy_upload"
        )
    
        if privacy_file is not None:
            df_original = pd.read_csv(privacy_file)
            st.success(f"✅ {len(df_original)} satırlık dosya yüklendi.")
    
            # PII Tespiti
            pii_cols = detect_pii_columns(df_original)
            if pii_cols:
                st.info(f"🔍 Tespit edilen kişisel veri sütunları: **{', '.join(pii_cols)}**")
            else:
                st.warning("⚠️ Otomatik PII tespiti yapılamadı. Manuel sütun seçebilirsiniz.")
    
            # Maskeleme yöntemi seçimi
            mask_method = st.selectbox(
                "Maskeleme Yöntemi Seçin:",
                ["hash", "partial", "redact"],
                format_func=lambda x: {
                    "hash": "🔐 SHA-256 Hash (Geri Döndürülemez)",
                    "partial": "🔤 Kısmi Maskeleme (İlk/Son Harf Görünür)",
                    "redact": "🚫 Tam Gizleme ([GİZLİ] ile değiştirilir)",
                }[x],
                key="mask_method",
            )
    
            if st.button("🛡️ Anonimleştir ve İndir", use_container_width=True, type="primary"):
                with st.spinner("Veriler anonimleştiriliyor..."):
                    df_anon = anonymize_dataframe(df_original, method=mask_method)
                    privacy_report = generate_privacy_report(df_original, df_anon)
    
                # Gizlilik Raporu
                st.markdown("### 📋 Gizlilik Raporu")
                priv_c1, priv_c2, priv_c3 = st.columns(3)
                priv_c1.metric("Toplam Satır", f"{privacy_report['toplam_satir']:,}")
                priv_c2.metric("Maskelenen Sütun", str(privacy_report['maskelenen_sutun_sayisi']))
                priv_c3.metric("KVKK Durumu", privacy_report['kvkk_uyumluluk'])
    
                # Önizleme
                st.markdown("### 👁️ Anonimleştirilmiş Veri Önizlemesi (İlk 10 Satır)")
                st.dataframe(df_anon.head(10), use_container_width=True)
    
                # İndirme
                csv_anon = df_anon.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Anonimleştirilmiş Veriyi İndir",
                    data=csv_anon,
                    file_name="anonim_veri.csv",
                    mime="text/csv",
                )
    
    # --- SEKME 11: DRİFT ANALİZİ ---
