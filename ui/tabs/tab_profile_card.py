import streamlit as st
from services.customer_profile_service import (
    compute_customer_value_breakdown,
    create_profile_card_fig,
    create_risk_history_chart,
    create_shap_waterfall,
    find_similar_customers,
)

def render_tab_profile_card(local_model=None, local_scaler=None, expected_features=None):
        st.subheader("👤 Müşteri 360° Profil Kartı")
        st.write(
            "Tekil Analiz sekmesinden analiz yapıldıktan sonra, müşterinin tüm bilgileri, "
            "risk detayları ve benzer müşteriler burada görüntülenir."
        )
    
        if st.session_state.current_customer is not None and st.session_state.base_risk is not None:
            cust = st.session_state.current_customer
            risk = st.session_state.base_risk
            risk_level = "Yüksek" if risk > 70 else "Orta" if risk > 40 else "Düşük"
    
            prof_col1, prof_col2 = st.columns([1, 1])
    
            with prof_col1:
                # Profil Kartı
                fig_card = create_profile_card_fig(cust, risk, risk_level)
                st.plotly_chart(fig_card, use_container_width=True)
    
            with prof_col2:
                # CLTV Bileşen Grafiği
                fig_cltv = compute_customer_value_breakdown(cust)
                st.plotly_chart(fig_cltv, use_container_width=True)
    
            st.write("---")
    
            # SHAP Waterfall
            if local_model is not None:
                st.markdown("### 🌊 SHAP Waterfall Analizi")
                fig_waterfall = create_shap_waterfall(cust, local_model, local_scaler, expected_features)
                if fig_waterfall is not None:
                    st.plotly_chart(fig_waterfall, use_container_width=True)
                else:
                    st.info("SHAP Waterfall hesaplanamadı.")
    
            st.write("---")
    
            # Risk Geçmişi
            if st.session_state.risk_history:
                st.markdown("### 📈 Oturum İçi Risk Analizi Geçmişi")
                fig_history = create_risk_history_chart(st.session_state.risk_history)
                if fig_history is not None:
                    st.plotly_chart(fig_history, use_container_width=True)
    
            st.write("---")
    
            # Benzer Müşteriler
            st.markdown("### 🔍 Benzer Profilli Müşteriler")
            n_similar = st.slider("Gösterilecek benzer müşteri sayısı:", 3, 10, 5, key="sim_n")
            similar_df = find_similar_customers(cust, n_neighbors=n_similar)
            if similar_df is not None:
                st.dataframe(similar_df, use_container_width=True)
            else:
                st.info("Veri seti bulunamadığı için benzer müşteriler gösterilemiyor.")
        else:
            st.warning(
                "⚠️ Lütfen önce '👤 Tekil Analiz' sekmesinden bir müşteri analizi yapın."
            )
    
    # --- SEKME 10: VERİ GİZLİLİĞİ (KVKK/GDPR) ---
