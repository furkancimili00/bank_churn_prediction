import sys
content = open("dashboard.py", "r", encoding="utf-8").read()

content = content.replace("from ui.tabs.tab_whatif_simulator import render_tab_whatif_simulator\n", "from ui.tabs.tab_whatif_simulator import render_tab_whatif_simulator\nfrom ui.i18n import init_i18n, t, render_language_and_theme_toggles\n")

# Replace TAB_DEFINITIONS
old_tabs = """TAB_DEFINITIONS = [
    DashboardTab("👤 Tekil Analiz", render_tab_single_analysis),
    DashboardTab("🧪 What-If", render_tab_whatif_simulator),
    DashboardTab("📂 Toplu Analiz", render_tab_batch_analysis),
    DashboardTab("📈 Performans", render_tab_performance),
    DashboardTab("🎯 Segmentasyon", render_tab_segmentation),
    DashboardTab("⚖️ Adillik", render_tab_fairness),
    DashboardTab("👤 Profil Kartı", render_tab_profile_card),
    DashboardTab("🔒 Gizlilik", render_tab_privacy),
    DashboardTab("📉 Drift Analizi", render_tab_drift),
    DashboardTab("📜 Denetim Günlüğü", render_tab_audit_logs),
]"""
# Note: Actually they have emojis, let's replace dynamically via a function override.
