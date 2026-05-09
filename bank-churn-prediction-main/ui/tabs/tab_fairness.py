import streamlit as st
from services.eda_service import load_default_dataset
from services.fairness_service import (
    compute_disparate_impact,
    compute_group_churn_rates,
    create_bias_summary_table,
    create_churn_rate_comparison_fig,
    create_disparate_impact_gauge,
    create_probability_distribution_fig,
)

def render_tab_fairness(local_model=None, local_scaler=None, expected_features=None):
        st.subheader("⚖️ Adillik ve Önyargı Analizi (Fairness/Bias)")
        st.write(
            "Modelin cinsiyet ve coğrafya bazında adil tahmin yapıp yapmadığını analiz edin. "
            "Tez hedefi: Disparate Impact < 1.2"
        )
    
        if local_model is not None:
            fair_df = load_default_dataset()
            if fair_df is not None:
                with st.spinner("Adillik analizi yapılıyor..."):
                    all_di_results = []
    
                    for group_col in ["Gender", "Geography"]:
                        group_stats = compute_group_churn_rates(
                            fair_df, local_model, local_scaler, expected_features, group_col
                        )
                        if group_stats is not None:
                            di_result = compute_disparate_impact(group_stats, group_col)
                            di_result["group_col"] = group_col
                            all_di_results.append(di_result)
    
                # Bias Özet Tablosu
                if all_di_results:
                    st.markdown("### 📋 Adillik Özet Raporu")
                    fig_bias_table = create_bias_summary_table(all_di_results)
                    st.plotly_chart(fig_bias_table, use_container_width=True)
    
                st.write("---")
    
                # Cinsiyet ve Coğrafya Analizi
                for group_col in ["Gender", "Geography"]:
                    st.markdown(f"### 🔍 {group_col} Bazında Analiz")
    
                    group_stats = compute_group_churn_rates(
                        fair_df, local_model, local_scaler, expected_features, group_col
                    )
    
                    if group_stats is not None:
                        di_result = compute_disparate_impact(group_stats, group_col)
    
                        fair_col1, fair_col2 = st.columns(2)
    
                        with fair_col1:
                            fig_bar = create_churn_rate_comparison_fig(group_stats, group_col)
                            st.plotly_chart(fig_bar, use_container_width=True)
    
                        with fair_col2:
                            fig_gauge = create_disparate_impact_gauge(di_result, group_col)
                            st.plotly_chart(fig_gauge, use_container_width=True)
    
                        # Violin Plot
                        fig_violin = create_probability_distribution_fig(
                            fair_df, local_model, local_scaler, expected_features, group_col
                        )
                        if fig_violin is not None:
                            st.plotly_chart(fig_violin, use_container_width=True)
    
                        st.write("---")
            else:
                st.warning("⚠️ Varsayılan veri seti bulunamadı.")
        else:
            st.error("❌ Model yüklenemedi.")
    
    # --- SEKME 9: MÜŞTERİ 360° PROFİL KARTI ---
