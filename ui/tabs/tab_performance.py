from ui.i18n import t
import streamlit as st
from services.eda_service import load_default_dataset
from services.model_metrics_service import (
    compute_all_metrics,
    create_confusion_matrix_fig,
    create_feature_importance_fig,
    create_metrics_comparison_table,
    create_precision_recall_fig,
    create_roc_curve_fig,
)

def render_tab_performance(local_model=None, local_scaler=None, expected_features=None):
        st.subheader(t("perf_title"))
        st.write(
            "Eğitilmiş XGBoost modelinin performans metriklerini, "
            "tez hedefleriyle karşılaştırmalı olarak inceleyin."
        )
    
        if local_model is not None:
            perf_df = load_default_dataset()
            if perf_df is not None:
                with st.spinner("Model metrikleri hesaplanıyor..."):
                    metrics = compute_all_metrics(
                        local_model, local_scaler, expected_features, perf_df
                    )
    
                if metrics is not None:
                    # Metrik Karşılaştırma Tablosu
                    st.markdown(t("perf_target"))
                    fig_table = create_metrics_comparison_table(metrics)
                    st.plotly_chart(fig_table, use_container_width=True)
    
                    st.write("---")
                    perf_col1, perf_col2 = st.columns(2)
    
                    # Confusion Matrix
                    with perf_col1:
                        st.markdown(t("perf_cm"))
                        fig_cm = create_confusion_matrix_fig(metrics["y_true"], metrics["y_pred"])
                        st.plotly_chart(fig_cm, use_container_width=True)
    
                    # Feature Importance
                    with perf_col2:
                        st.markdown(t("perf_feat_imp"))
                        fig_fi = create_feature_importance_fig(local_model, expected_features)
                        if fig_fi is not None:
                            st.plotly_chart(fig_fi, use_container_width=True)
                        else:
                            st.info(t("perf_no_feat_imp"))
    
                    st.write("---")
                    roc_col, pr_col = st.columns(2)
    
                    # ROC Eğrisi
                    with roc_col:
                        st.markdown(t("perf_roc"))
                        fig_roc = create_roc_curve_fig(metrics["y_true"], metrics["y_proba"])
                        st.plotly_chart(fig_roc, use_container_width=True)
    
                    # Precision-Recall Eğrisi
                    with pr_col:
                        st.markdown(t("perf_pr"))
                        fig_pr = create_precision_recall_fig(metrics["y_true"], metrics["y_proba"])
                        st.plotly_chart(fig_pr, use_container_width=True)
                else:
                    st.error(t("perf_err_metrics"))
            else:
                st.warning(t("perf_no_data"))
        else:
            st.error(t("perf_no_model"))
    
    # --- SEKME 7: MÜŞTERİ SEGMENTASYONU ---
