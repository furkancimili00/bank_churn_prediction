from ui.i18n import t
import streamlit as st
import pandas as pd
from services.audit_service import clear_audit_log, get_event_summary, get_recent_events

def render_tab_audit_logs(local_model=None, local_scaler=None, expected_features=None):
        st.subheader(t("audit_title"))
        st.write(t("audit_desc"))
    
        summary = get_event_summary()
    
        aud_c1, aud_c2, aud_c3 = st.columns(3)
        aud_c1.metric("Toplam Kayıt", summary.get("toplam_kayit", 0))
        aud_c2.metric("Son Olay", summary.get("son_olay", "—")[:19] if summary.get("son_olay") else "—")
        event_types = summary.get("olay_tipleri", {})
        aud_c3.metric("Olay Türü Sayısı", len(event_types))
    
        if event_types:
            st.markdown(t("audit_dist"))
            import plotly.express as px
            df_events = pd.DataFrame([
                {"Olay Türü": k, "Sayı": v} for k, v in event_types.items()
            ])
            fig_ev = px.bar(df_events, x="Olay Türü", y="Sayı", color="Olay Türü")
            fig_ev.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_ev, use_container_width=True)
    
        st.markdown(t("audit_recent"))
        n_events = st.slider(t("audit_num_logs"), 5, 100, 20, key="audit_n")
        events = get_recent_events(limit=n_events)
        if events:
            df_log = pd.DataFrame(events)
            st.dataframe(df_log, use_container_width=True)
        else:
            st.info(t("audit_no_logs"))
    
        if st.button(t("audit_btn_clear"), type="secondary"):
            clear_audit_log()
            st.success(t("audit_cleared"))
            st.rerun()
    
