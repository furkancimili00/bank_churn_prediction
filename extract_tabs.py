import os

def extract_tabs():
    with open('dashboard.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    tabs = {
        "tab_single_analysis.py": "with tab1:",
        "tab_whatif_simulator.py": "with tab2:",
        "tab_batch_analysis.py": "with tab3:",
        "tab_management_report.py": "with tab4:",
        "tab_eda.py": "with tab5:",
        "tab_performance.py": "with tab6:",
        "tab_segmentation.py": "with tab7:",
        "tab_fairness.py": "with tab8:",
        "tab_profile_card.py": "with tab9:",
        "tab_privacy.py": "with tab10:",
        "tab_drift.py": "with tab11:",
        "tab_audit_logs.py": "with tab12:"
    }

    current_tab = None
    tab_content = {k: [] for k in tabs.keys()}
    
    # We will just write a function render_tabX() in each file
    
    for i, line in enumerate(lines):
        if "with tab" in line and line.strip().endswith(":"):
            for filename, identifier in tabs.items():
                if identifier in line:
                    current_tab = filename
                    break
            continue
            
        if current_tab:
            # Check if we moved out of the `with tabX:` block
            # In Streamlit, everything under `with tab:` is indented by at least 4 spaces.
            if line.strip() != "" and not line.startswith("    "):
                # We moved out of the tab (e.g. to a new tab)
                current_tab = None
            else:
                if current_tab:
                    # Dedent by 4 spaces
                    if line.startswith("    "):
                        tab_content[current_tab].append(line[4:])
                    else:
                        tab_content[current_tab].append(line)

    os.makedirs("ui/tabs", exist_ok=True)
    for filename, content in tab_content.items():
        with open(os.path.join("ui/tabs", filename), 'w', encoding='utf-8') as f:
            f.write("import streamlit as st\n")
            f.write("import pandas as pd\n")
            f.write("import plotly.graph_objects as go\n")
            f.write("import numpy as np\n")
            f.write("from core.utils import preprocess_data\n")
            f.write("from agents.churn_agent import run_agent, generate_management_report\n")
            f.write("from services.prediction import load_local_model, get_shap_explainer, make_prediction, make_batch_prediction\n")
            f.write("from services.eda_service import load_default_dataset, create_correlation_heatmap, create_distribution_histograms, create_churn_boxplots, create_categorical_analysis, create_churn_rate_by_category, get_summary_statistics\n")
            f.write("from services.model_metrics_service import compute_all_metrics, create_confusion_matrix_fig, create_roc_curve_fig, create_precision_recall_fig, create_feature_importance_fig, create_metrics_comparison_table\n")
            f.write("from services.segmentation_service import find_optimal_k, perform_segmentation, create_pca_scatter, create_segment_profile, create_segment_summary_table, create_segment_churn_bar\n")
            f.write("from services.fairness_service import compute_group_churn_rates, compute_disparate_impact, create_churn_rate_comparison_fig, create_disparate_impact_gauge, create_probability_distribution_fig, create_bias_summary_table\n")
            f.write("from services.customer_profile_service import create_profile_card_fig, create_shap_waterfall, find_similar_customers, create_risk_history_chart, compute_customer_value_breakdown\n")
            f.write("from services.data_privacy import anonymize_dataframe, generate_privacy_report, detect_pii_columns\n")
            f.write("from services.drift_service import analyze_drift, create_drift_summary_table, create_drift_distribution_fig\n")
            f.write("from services.audit_service import log_event, get_recent_events, get_event_summary, clear_audit_log\n")
            f.write("\n")
            f.write(f"def render_{filename.split('.')[0]}(")
            f.write("local_model=None, local_scaler=None, expected_features=None):\n")
            if not content:
                f.write("    pass\n")
            for line in content:
                f.write("    " + line)
                
    print("Tabs extracted successfully.")

if __name__ == "__main__":
    extract_tabs()
