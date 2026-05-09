import pandas as pd
import skops.io as sio
import shap
from core.utils import preprocess_data

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

try:
    print("Creating explainer...")
    explainer = shap.TreeExplainer(model)
    print("Explainer created. Getting shap values...")
    shap_values = explainer.shap_values(scaled_input_shap, check_additivity=False)
    print("SHAP Values type:", type(shap_values))
    if isinstance(shap_values, list):
        print("List length:", len(shap_values))
        print("Element shape:", shap_values[0].shape)
    else:
        print("Array shape:", shap_values.shape)
except Exception as e:
    import traceback
    traceback.print_exc()
