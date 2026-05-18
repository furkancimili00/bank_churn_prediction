from ui.i18n import t
import streamlit as st
from agents.churn_agent import generate_management_report

def render_tab_management_report(local_model=None, local_scaler=None, expected_features=None):
        st.subheader(t("report_title"))
    
        if "results_df" in st.session_state:
            st.info(t("report_ready"))
    
            if st.button(t("report_btn"), use_container_width=True, type="primary"):
                with st.spinner("RAG Modülü: Rapor oluşturuluyor..."):
                    report_md = generate_management_report(st.session_state.results_df)
                    st.session_state.management_report = report_md
    
            if "management_report" in st.session_state:
                st.markdown(st.session_state.management_report)
    
                st.download_button(
                    label="📄 Raporu Markdown Olarak İndir",
                    data=st.session_state.management_report,
                    file_name="yonetim_raporu.md",
                    mime="text/markdown"
                )
        else:
            st.warning(t("report_req"))
    
    # --- SEKME 5: KEŞİFSEL VERİ ANALİZİ (EDA) ---
