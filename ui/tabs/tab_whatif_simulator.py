from ui.i18n import t
import streamlit as st
import plotly.graph_objects as go
from services.prediction import make_prediction

def render_tab_whatif_simulator(local_model=None, local_scaler=None, expected_features=None):
        st.subheader(t("wi_title"))
        if st.session_state.current_customer is not None:
            cust = st.session_state.current_customer
            base_risk = st.session_state.base_risk
    
            st.info(
                t("wi_desc")
            )
    
            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                st.markdown(t("wi_fin"))
                new_balance = st.slider(
                    t("wi_bal"),
                    min_value=0.0,
                    max_value=250000.0,
                    value=float(cust["Balance"]),
                    step=1000.0,
                    key="sim_bal",
                )
                new_est_salary = st.slider(
                    t("wi_sal"),
                    min_value=0.0,
                    max_value=200000.0,
                    value=float(cust["EstimatedSalary"]),
                    step=1000.0,
                    key="sim_sal",
                )
            with sim_col2:
                st.markdown(t("wi_bank"))
                new_products = st.slider(
                    t("wi_prod"),
                    1,
                    4,
                    value=int(cust["NumOfProducts"]),
                    key="sim_prod",
                )
                new_active = st.selectbox(
                    t("wi_active"),
                    [1, 0],
                    index=0 if cust["IsActiveMember"] == 1 else 1,
                    key="sim_act",
                )
                new_crcard = st.selectbox(
                    t("wi_cc"),
                    [1, 0],
                    index=0 if cust["HasCrCard"] == 1 else 1,
                    key="sim_cr",
                )
    
            if st.button(
                t("wi_btn"),
                type="primary",
                use_container_width=True,
            ):
                sim_data = cust.copy()
                sim_data.update(
                    {
                        "Balance": new_balance,
                        "EstimatedSalary": new_est_salary,
                        "IsActiveMember": new_active,
                        "HasCrCard": new_crcard,
                        "NumOfProducts": new_products,
                    }
                )
    
                # SİMÜLASYONDA DA YEREL TAHMİN KULLANILIYOR
                with st.spinner("Simülasyon hesaplanıyor..."):
                    res_sim = make_prediction(
                        sim_data, local_model, local_scaler, expected_features
                    )
                    new_risk = res_sim["churn_ihtimali"] * 100
                    diff = new_risk - base_risk
    
                st.write("---")
                st.subheader(t("wi_results"))
    
                res_sim_col1, res_sim_col2 = st.columns(2)
    
                with res_sim_col1:
                    st.metric(label="Mevcut Ayrılma Riski", value=f"%{base_risk:.1f}")
                    if diff < 0:
                        st.metric(
                            label="Simüle Edilen Yeni Risk",
                            value=f"%{new_risk:.1f}",
                            delta=f"{diff:.1f} Puan (İyileşme)",
                            delta_color="normal",
                        )
                    else:
                        st.metric(
                            label="Simüle Edilen Yeni Risk",
                            value=f"%{new_risk:.1f}",
                            delta=f"+{diff:.1f} Puan (Kötüleşme)",
                            delta_color="inverse",
                        )
    
                with res_sim_col2:
                    # Basit bir çubuk grafik ile karşılaştırma
                    fig_comp = go.Figure()
                    fig_comp.add_trace(
                        go.Bar(
                            x=["Mevcut Durum", "Simülasyon"],
                            y=[base_risk, new_risk],
                            marker_color=[
                                "salmon",
                                "lightgreen" if diff < 0 else "red",
                            ],
                            text=[f"%{base_risk:.1f}", f"%{new_risk:.1f}"],
                            textposition="auto",
                        )
                    )
                    fig_comp.update_layout(
                        title="Risk Karşılaştırması",
                        yaxis_title="Ayrılma İhtimali (%)",
                        yaxis=dict(range=[0, 100]),
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
    
        else:
            st.warning(
                t("wi_req")
            )
    
    # --- SEKM 3: TOPLU MÜŞTERİ YÜKLEME ---
