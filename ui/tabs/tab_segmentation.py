from ui.i18n import t
import streamlit as st
from services.eda_service import load_default_dataset
from services.segmentation_service import (
    create_pca_scatter,
    create_segment_churn_bar,
    create_segment_profile,
    create_segment_summary_table,
    find_optimal_k,
    perform_segmentation,
)

def render_tab_segmentation(local_model=None, local_scaler=None, expected_features=None):
        st.subheader(t("seg_title"))
        st.write(
            "Müşterilerinizi davranış ve demografik özelliklerine göre otomatik segmentlere ayırın. "
            "Her segmentin risk profilini ve özelliklerini keşfedin."
        )
    
        seg_df = load_default_dataset()
        if seg_df is not None:
            # Elbow Method
            with st.expander("📀 Optimum Küme Sayısı Seçimi (Elbow Method)", expanded=False):
                fig_elbow = find_optimal_k(seg_df)
                st.plotly_chart(fig_elbow, use_container_width=True)
                st.caption("Grafiğin dirsek (elbow) noktası, optimum küme sayısını gösterir.")
    
            n_clusters = st.slider(
                t("seg_k"), min_value=2, max_value=6, value=3, key="seg_k"
            )
    
            if st.button(t("seg_btn"), use_container_width=True, type="primary"):
                with st.spinner("Kümeleme analizi yapılıyor..."):
                    df_seg, X_scaled, _ = perform_segmentation(seg_df, n_clusters)
    
                    # Özet Tablosu
                    st.markdown(t("seg_summary"))
                    fig_summary = create_segment_summary_table(df_seg)
                    st.plotly_chart(fig_summary, use_container_width=True)
    
                    st.write("---")
                    seg_col1, seg_col2 = st.columns(2)
    
                    # PCA Scatter
                    with seg_col1:
                        st.markdown(t("seg_pca"))
                        fig_pca = create_pca_scatter(df_seg, X_scaled)
                        st.plotly_chart(fig_pca, use_container_width=True)
    
                    # Segment Churn Oranları
                    with seg_col2:
                        fig_churn_bar = create_segment_churn_bar(df_seg)
                        if fig_churn_bar is not None:
                            st.markdown(t("seg_rate"))
                            st.plotly_chart(fig_churn_bar, use_container_width=True)
    
                    st.write("---")
                    # Radar Profil
                    st.markdown(t("seg_radar"))
                    fig_radar = create_segment_profile(df_seg)
                    st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.warning(t("seg_no_data"))
    
    # --- SEKME 8: ADİLLİK VE ÖNYARGI (FAIRNESS) ---
