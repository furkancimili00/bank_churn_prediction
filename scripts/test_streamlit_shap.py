import streamlit as st
import pandas as pd
import skops.io as sio
import shap
from core.utils import preprocess_data
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

st.write("Starting SHAP Explainer test...")

try:
    untrusted = sio.get_untrusted_types(file="churn_thesis_model.skops")
    model_pack = sio.load("churn_thesis_model.skops", trusted=untrusted)
    model = model_pack["model"]
    scaler = model_pack["scaler"]
    expected_features = model_pack["features"]

    data_dict = {
        "CreditScore": 650,
        "Geography": "France",
        "Gender": "Male",
        "Age": 40,
        "Tenure": 5,
        "Balance": 50000.0,
        "NumOfProducts": 1,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 60000.0,
    }

    df_input_shap = pd.DataFrame([data_dict])
    scaled_input_shap = preprocess_data(df_input_shap, expected_features, scaler)
    
    st.write("Creating explainer...")
    explainer = shap.TreeExplainer(model)
    st.write("Explainer created. Getting shap values...")
    shap_values = explainer.shap_values(scaled_input_shap, check_additivity=False)
    st.write("SHAP Values Shape:", shap_values.shape)
    st.success("Test completed successfully without errors!")
except Exception as e:
    st.error("Error occurred!")
    import traceback
    st.text(traceback.format_exc())
