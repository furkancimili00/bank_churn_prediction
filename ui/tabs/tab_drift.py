from ui.i18n import t
import streamlit as st
import pandas as pd
from services.drift_service import (
    analyze_drift,
    create_drift_distribution_fig,
    create_drift_summary_table,
)
from services.eda_service import load_default_dataset

def render_tab_drift(local_model=None, local_scaler=None, expected_features=None):
        st.subheader(t("drift_title"))
        st.write(
            "Yeni yüklediğiniz veriyi eğitim verisine kıyaslayın. "
            "PSI ve KS testleri ile dağılım kaymalarını tespit edin."
        )
    
        drift_file = st.file_uploader(
            t("drift_upload"), type=["csv"], key="drift_upload"
        )
    
        ref_df = load_default_dataset()
        if drift_file is not None and ref_df is not None:
            cur_df = pd.read_csv(drift_file)
            st.success(f"✅ {len(cur_df)} satırlık dosya yüklendi. Referans: {len(ref_df)} satır.")
    
            with st.spinner("Drift analizi yapılıyor..."):
                drift_results = analyze_drift(ref_df, cur_df)
    
            if drift_results:
                # Özet bilgi kartları
                drifted = sum(1 for r in drift_results if "Kritik" in r["severity"] or "Uyarı" in r["severity"])
                dr_c1, dr_c2, dr_c3 = st.columns(3)
                dr_c1.metric("İncelenen Özellik", len(drift_results))
                dr_c2.metric("Drift Tespit Edilen", drifted)
                dr_c3.metric("Durum", "⚠️ Drift Var" if drifted > 0 else "✅ Normal")
    
                # Drift Tablosu
                fig_drift = create_drift_summary_table(drift_results)
                st.plotly_chart(fig_drift, use_container_width=True)
    
                # Dağılım Karşılaştırmaları
                st.markdown(t("drift_dist_comp"))
                drifted_features = [r["feature"] for r in drift_results if r["psi"] > 0.05]
                if not drifted_features:
                    drifted_features = [drift_results[0]["feature"]] if drift_results else []
    
                for feat in drifted_features[:4]:
                    fig_dist = create_drift_distribution_fig(ref_df, cur_df, feat)
                    st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info(t("drift_no_num_cols"))
        elif drift_file is None:
            st.info(t("drift_upload_req"))
        else:
            st.warning(t("drift_no_ref"))
    
    # --- SEKME 12: DENETİM GÜNLÜĞÜ ---
