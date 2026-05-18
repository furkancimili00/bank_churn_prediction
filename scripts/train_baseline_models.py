"""
Baseline Modeller ile Karşılaştırmalı Eğitim (Tez Kapsamı)
Tez önerisinde bahsedilen Logistic Regression ve Random Forest modellerini
ADASYN ve SMOTE kullanarak XGBoost ile karşılaştırır.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE, ADASYN
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score, f1_score
from core.utils import preprocess_data
from core.logging_config import get_logger
import skops.io as sio

logger = get_logger(__name__)


def evaluate_models():
    """Çeşitli modelleri ADASYN/SMOTE ile karşılaştırır."""
    df = pd.read_csv("Churn_Modelling.csv")

    X = df.drop(columns=["RowNumber", "CustomerId", "Surname", "Exited"])
    y = df["Exited"]

    untrusted = sio.get_untrusted_types(file="churn_thesis_model.skops")
    model_pack = sio.load("churn_thesis_model.skops", trusted=untrusted)
    scaler = model_pack["scaler"]
    features = model_pack["features"]

    X_preprocessed = preprocess_data(X, features, scaler)

    # Train/Test ayırma
    X_train, X_test, y_train, y_test = train_test_split(
        X_preprocessed, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "Random Forest": RandomForestClassifier(random_state=42, n_estimators=100),
        "XGBoost": XGBClassifier(random_state=42, eval_metric="logloss"),
    }

    samplers = {
        "SMOTE": SMOTE(random_state=42),
        "ADASYN": ADASYN(random_state=42),
    }

    logger.info("Karşılaştırmalı Model Eğitimi Başlıyor (Tez Kapsamı)")
    
    results = []

    for sampler_name, sampler in samplers.items():
        logger.info(f"\nVeri Temsili (Oversampling): {sampler_name}")
        X_res, y_res = sampler.fit_resample(X_train, y_train)

        for model_name, model in models.items():
            model.fit(X_res, y_res)
            
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
            
            f1 = f1_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_proba)
            
            results.append({
                "Sampler": sampler_name,
                "Model": model_name,
                "F1-Score": f1,
                "ROC-AUC": roc_auc
            })
            
            logger.info(f"Model: {model_name:20s} | F1: {f1:.4f} | ROC-AUC: {roc_auc:.4f}")

    results_df = pd.DataFrame(results)
    results_df.to_csv("docs/thesis_paper/baseline_comparison_results.csv", index=False)
    logger.success("Karşılaştırma sonuçları 'docs/thesis_paper/baseline_comparison_results.csv' dosyasına kaydedildi.")

if __name__ == "__main__":
    evaluate_models()