import sys
content = open("dashboard.py", "r", encoding="utf-8").read()

content = content.replace(
    'from ui.tabs.tab_whatif_simulator import render_tab_whatif_simulator\n\nos.environ["USE_TF"] = "NO"',
    'from ui.tabs.tab_whatif_simulator import render_tab_whatif_simulator\nfrom ui.i18n import init_i18n, t, render_language_and_theme_toggles\n\nos.environ["USE_TF"] = "NO"'
)

# Fix TAB_DEFINITIONS
old_tabs = """TAB_DEFINITIONS = [
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
]"""
new_tabs = """def get_tab_definitions():
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
    ]"""
content = content.replace(old_tabs, new_tabs)

# Fix login screen
content = content.replace(
    '"<h3 style=\'text-align: center;\'>Kurumsal Yönetici Girişi</h3>"',
    'f"<h3 style=\'text-align: center;\'>{t(\"login_title\")}</h3>"'
)
content = content.replace('st.text_input("Kullanıcı Adı")', 'st.text_input(t("username"))')
content = content.replace('st.text_input("Şifre", type="password")', 'st.text_input(t("password"), type="password")')
content = content.replace('st.button("Sisteme Giriş Yap", use_container_width=True)', 'st.button(t("login_btn"), use_container_width=True)')
content = content.replace('st.success("Giriş başarılı.")', 'st.success(t("login_success"))')
content = content.replace('st.error("Hatalı kullanıcı adı veya şifre.")', 'st.error(t("login_error"))')

# Fix sidebar
content = content.replace('st.sidebar.title("Yönetici Menüsü")', 'st.sidebar.title(t("menu_title"))')
content = content.replace('st.sidebar.info("Hoş geldiniz, **Şube Müdürü**")', 'st.sidebar.info(f"{t(\\"welcome\\")} **{t(\\"manager\\")}**")')
content = content.replace('st.sidebar.subheader("ℹ️ Uygulama Hakkında")', 'st.sidebar.subheader(t("about"))')
content = content.replace('"Bu panel, müşteri terk riskini analiz etmek, simüle etmek ve toplu "\n        "değerlendirmeler yapmak için geliştirilmiştir."', 't("about_desc1")')
content = content.replace('st.sidebar.write("Yapay zeka destekli tahmin ve kampanya öneri sistemleri içerir.")', 'st.sidebar.write(t("about_desc2"))')
content = content.replace('st.sidebar.subheader("📊 Genel Metrikler")', 'st.sidebar.subheader(t("metrics"))')
content = content.replace('label="Sistem Durumu", value="Aktif", delta="Model Yüklü"', 'label=t("sys_status"), value=t("active"), delta=t("model_loaded")')
content = content.replace('st.sidebar.button("🚪 Güvenli Çıkış Yap")', 'st.sidebar.button(t("logout"))')
content = content.replace('st.sidebar.subheader("🎓 Proje Hakkında")', 'st.sidebar.subheader(t("project_about"))')
content = content.replace('render_sidebar()\n    st.title("🏦 Şube Müdürü Müşteri Risk Analiz Paneli")', 'render_sidebar()\n    render_language_and_theme_toggles()\n    st.title(t("main_title"))')

# Replace dynamic TAB iterations
content = content.replace(
    'tabs = st.tabs([tab_definition.title for tab_definition in TAB_DEFINITIONS])\n    for tab_container, tab_definition in zip(tabs, TAB_DEFINITIONS):',
    'tab_defs = get_tab_definitions()\n    tabs = st.tabs([td.title for td in tab_defs])\n    for tab_container, tab_definition in zip(tabs, tab_defs):'
)

# initialize_session_state replacement
old_init = """def initialize_session_state() -> None:
    \"\"\"Dashboard için gerekli oturum değişkenlerini başlatır.\"\"\"
    st.session_state.setdefault("logged_in", False)"""
new_init = """def initialize_session_state() -> None:
    \"\"\"Dashboard için gerekli oturum değişkenlerini başlatır.\"\"\"
    init_i18n()
    st.session_state.setdefault("logged_in", False)"""
content = content.replace(old_init, new_init)

open("dashboard.py", "w", encoding="utf-8").write(content)
print("Updated dashboard.py!")
