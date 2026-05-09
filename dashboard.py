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

os.environ["USE_TF"] = "NO"
os.environ["USE_TORCH"] = "NO"


@dataclass(frozen=True)
class DashboardTab:
    """Dashboard sekme başlığı ve render fonksiyonunu taşır."""

    title: str
    renderer: Callable[[Any, Any, list[str]], None]


TAB_DEFINITIONS = [
    DashboardTab("👤 Tekil Analiz", render_tab_single_analysis),
    DashboardTab("🧪 What-If", render_tab_whatif_simulator),
    DashboardTab("📂 Toplu Analiz", render_tab_batch_analysis),
    DashboardTab("📝 Yönetim Raporu", render_tab_management_report),
    DashboardTab("📈 EDA", render_tab_eda),
    DashboardTab("🏆 Performans", render_tab_performance),
    DashboardTab("🎯 Segmentasyon", render_tab_segmentation),
    DashboardTab("⚖️ Adillik", render_tab_fairness),
    DashboardTab("👤 Profil Kartı", render_tab_profile_card),
    DashboardTab("🔒 Gizlilik", render_tab_privacy),
    DashboardTab("📉 Drift Analizi", render_tab_drift),
    DashboardTab("📜 Denetim Günlüğü", render_tab_audit_logs),
]

local_model, local_scaler, expected_features = load_local_model()

st.set_page_config(page_title="Banka Churn Risk Paneli", page_icon="🏦", layout="wide")


def initialize_session_state() -> None:
    """Dashboard için gerekli oturum değişkenlerini başlatır."""
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
            "<h3 style='text-align: center;'>Kurumsal Yönetici Girişi</h3>",
            unsafe_allow_html=True,
        )
        st.write("---")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")

        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if (
                username == st.secrets["auth"]["username"]
                and password == st.secrets["auth"]["password"]
            ):
                st.session_state.logged_in = True
                st.success("Giriş başarılı.")
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre.")


def render_sidebar() -> None:
    """Dashboard yan menüsünü render eder."""
    st.sidebar.title("Yönetici Menüsü")
    st.sidebar.info("Hoş geldiniz, **Şube Müdürü**")

    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Uygulama Hakkında")
    st.sidebar.write(
        "Bu panel, müşteri terk riskini analiz etmek, simüle etmek ve toplu "
        "değerlendirmeler yapmak için geliştirilmiştir."
    )
    st.sidebar.write("Yapay zeka destekli tahmin ve kampanya öneri sistemleri içerir.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Genel Metrikler")
    st.sidebar.metric(label="Sistem Durumu", value="Aktif", delta="Model Yüklü")

    if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
        log_event("logout", {"user": "admin"})
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎓 Proje Hakkında")
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
    st.title("🏦 Şube Müdürü Müşteri Risk Analiz Paneli")

    tabs = st.tabs([tab_definition.title for tab_definition in TAB_DEFINITIONS])
    for tab_container, tab_definition in zip(tabs, TAB_DEFINITIONS):
        with tab_container:
            tab_definition.renderer(local_model, local_scaler, expected_features)


if __name__ == "__main__":
    initialize_session_state()
    if st.session_state.logged_in:
        main_dashboard()
    else:
        login_screen()
