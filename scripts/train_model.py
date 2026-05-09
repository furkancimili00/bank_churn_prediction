"""
Müşteri Kayıp (Churn) Model Eğitimi ve Optimizasyonu
Bu betik, GridSearchCV kullanarak XGBoost sınıflandırıcısı için
hiper-parametre optimizasyonu yapar ve en iyi modeli .skops formatında kaydeder.
"""

import skops.io as sio
import pandas as pd
from sklearn.model_selection import GridSearchCV, train_test_split
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, roc_auc_score
from core.utils import preprocess_data
from core.logging_config import get_logger

logger = get_logger(__name__)


def load_data(filepath: str = "Churn_Modelling.csv") -> pd.DataFrame:
    """Verisetini yükler."""
    return pd.read_csv(filepath)


def train_and_optimize():
    """Modeli eğitir ve optimize eder."""
    # Mevcut modelden scaler ve özellikleri çekmek
    # Böylece production sistemleriyle tam uyum sağlanır
    try:
        untrusted = sio.get_untrusted_types(file="churn_thesis_model.skops")
        model_pack = sio.load("churn_thesis_model.skops", trusted=untrusted)
        scaler = model_pack["scaler"]
        features = model_pack["features"]

        # Scaler'ı diske ayrıca kaydediyoruz
        sio.dump(scaler, "scaler.skops")
        logger.info("Scaler 'scaler.skops' olarak diske kaydedildi.")
    except Exception as e:
        logger.error(f"Mevcut model yüklenemedi: {e}")
        return

    try:
        df = load_data()
    except FileNotFoundError:
        logger.warning(
            "Veriseti bulunamadı, lütfen 'Churn_Modelling.csv' dosyasını çalışma dizinine ekleyin. Scaler mevcut modelden çıkartıldı."
        )
        return

    X = df.drop(columns=["RowNumber", "CustomerId", "Surname", "Exited"])
    y = df["Exited"]

    # Veriyi ön işleme sokma
    X_preprocessed = preprocess_data(X, features, scaler)

    # Train/Test ayırma
    X_train, X_test, y_train, y_test = train_test_split(
        X_preprocessed, y, test_size=0.2, random_state=42, stratify=y
    )

    # Optimizasyon için GridSearchCV
    xgb = XGBClassifier(random_state=42, eval_metric="logloss")

    param_grid = {
        "n_estimators": [100, 500, 1000],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.01, 0.05, 0.1],
        "subsample": [0.8, 1.0],
        "colsample_bytree": [0.8, 1.0],
        "scale_pos_weight": [sum(y_train == 0) / sum(y_train == 1)],
    }

    logger.info("Hiperparametre optimizasyonu başlatılıyor...")
    grid_search = GridSearchCV(
        estimator=xgb,
        param_grid=param_grid,
        cv=5,
        n_jobs=-1,
        scoring="roc_auc",
        verbose=1,
    )
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_

    logger.info(f"En iyi parametreler: {grid_search.best_params_}")

    # Test setinde değerlendirme
    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]

    logger.info("Sınıflandırma Raporu (Classification Report):")
    logger.info(f"\n{classification_report(y_test, y_pred)}")
    logger.info(f"Test Seti ROC AUC Skoru: {roc_auc_score(y_test, y_proba)}")

    # Modeli diske yazma
    sio.dump(
        {"model": best_model, "scaler": scaler, "features": features},
        "churn_thesis_model.skops",
    )

    # Yeni eğitilen scaler'ı da diske kaydediyoruz
    sio.dump(scaler, "scaler.skops")

    logger.success("Model başarıyla 'churn_thesis_model.skops' konumuna kaydedildi.")


if __name__ == "__main__":
    train_and_optimize()
