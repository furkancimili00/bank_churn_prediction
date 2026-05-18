import os
from dataclasses import dataclass
from typing import Any, Callable

import streamlit as st

from services.audit_service import log_event
from services.prediction import load_local_model
from ui.tabs.tab_audit_logs import render_tab_audit_logs
from ui.tabs.tab_batch_analysis import render_tab_batch_analysis
from ui.tabs.tab_drift import render_tab_drift
from ui.tabs.tab_eda import render_tab_eda
from ui.tabs.tab_fairness import render_tab_fairness
from ui.tabs.tab_management_report import render_tab_management_report
from ui.tabs.tab_performance import render_tab_performance
from ui.tabs.tab_privacy import render_tab_privacy
from ui.tabs.tab_profile_card import render_tab_profile_card
from ui.tabs.tab_segmentation import render_tab_segmentation
from ui.tabs.tab_single_analysis import render_tab_single_analysis
from ui.tabs.tab_whatif_simulator import render_tab_whatif_simulator
from ui.i18n import init_i18n, t, render_language_and_theme_toggles
from ui.ai_assistant import render_floating_assistant

os.environ["USE_TF"] = "NO"
os.environ["USE_TORCH"] = "NO"


@dataclass(frozen=True)
class DashboardTab:
    """Dashboard sekme başlığı ve render fonksiyonunu taşır."""

    title: str
    renderer: Callable[[Any, Any, list[str]], None]


def get_tab_definitions():
    return [
        DashboardTab(t("tab_single"), render_tab_single_analysis),
        DashboardTab(t("tab_whatif"), render_tab_whatif_simulator),
        DashboardTab(t("tab_batch"), render_tab_batch_analysis),
        DashboardTab(t("tab_report"), render_tab_management_report),
        DashboardTab(t("tab_eda"), render_tab_eda),
        DashboardTab(t("tab_perf"), render_tab_performance),
        DashboardTab(t("tab_segment"), render_tab_segmentation),
        DashboardTab(t("tab_fair"), render_tab_fairness),
        DashboardTab(t("tab_profile"), render_tab_profile_card),
        DashboardTab(t("tab_privacy"), render_tab_privacy),
        DashboardTab(t("tab_drift"), render_tab_drift),
        DashboardTab(t("tab_audit"), render_tab_audit_logs),
    ]

local_model, local_scaler, expected_features = load_local_model()

st.set_page_config(page_title="Banka Churn Risk Paneli", page_icon="🏦", layout="wide")


def initialize_session_state() -> None:
    """Dashboard için gerekli oturum değişkenlerini başlatır."""
    init_i18n()
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("current_customer", None)
    st.session_state.setdefault("base_risk", None)
    st.session_state.setdefault("risk_history", [])


def login_screen() -> None:
    """Yönetici giriş ekranını render eder."""
    _, center_column, _ = st.columns([1, 1, 1])
    with center_column:
        st.markdown("<h1 style='text-align: center;'>🏦</h1>", unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='text-align: center;'>{t("login_title")}</h3>",
            unsafe_allow_html=True,
        )
        st.write("---")
        username = st.text_input(t("username"))
        password = st.text_input(t("password"), type="password")

        if st.button(t("login_btn"), use_container_width=True):
            if (
                username == st.secrets["auth"]["username"]
                and password == st.secrets["auth"]["password"]
            ):
                st.session_state.logged_in = True
                st.success(t("login_success"))
                st.rerun()
            else:
                st.error(t("login_error"))


def render_sidebar() -> None:
    """Dashboard yan menüsünü render eder."""
    st.sidebar.title(t("menu_title"))
    st.sidebar.info(f'{t("welcome")} **{t("manager")}**')

    st.sidebar.markdown("---")
    st.sidebar.subheader(t("about"))
    st.sidebar.write(
        t("about_desc1")
    )
    st.sidebar.write(t("about_desc2"))

    st.sidebar.markdown("---")
    st.sidebar.subheader(t("metrics"))
    st.sidebar.metric(label=t("sys_status"), value=t("active"), delta=t("model_loaded"))

    if st.sidebar.button(t("logout")):
        log_event("logout", {"user": "admin"})
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader(t("project_about"))
    st.sidebar.markdown(
        """
        **Banka Müşteri Churn Tahmin Platformu**

        🎯 **Hedef Metrikler:**
        - F1 Score > 0.85
        - ROC-AUC > 0.90
        - API Yanıt < 1s

        ⚙️ **Teknoloji Yığını:**
        - XGBoost + SHAP
        - FastAPI + Streamlit
        - LangGraph + Loguru
        - Docker + CI/CD

        🌍 **SDG Uyumluluk:**
        - SDG 8: İnsana Yakışır İş
        - SDG 10: Eşitsizliklerin Azaltılması

        *v2.0.0 - Kurumsal Karar Destek Platformu*
        """
    )


def main_dashboard() -> None:
    """Ana dashboard sekmelerini ve ortak layout'u render eder."""
    render_sidebar()
    render_language_and_theme_toggles()
    st.title(t("main_title"))

    tab_defs = get_tab_definitions()
    tabs = st.tabs([td.title for td in tab_defs])
    for tab_container, tab_definition in zip(tabs, tab_defs):
        with tab_container:
            tab_definition.renderer(local_model, local_scaler, expected_features)
            
    # Sağ alt köşede yüzen AI Asistanı render et
    render_floating_assistant()


if __name__ == "__main__":
    initialize_session_state()
    if st.session_state.logged_in:
        main_dashboard()
    else:
        login_screen()
