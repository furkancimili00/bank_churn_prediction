"""Churn tahmin is mantigini merkezi hale getiren servis."""

from typing import Any, Optional

import numpy as np
import pandas as pd

from core.utils import preprocess_data
from domain.risk import HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD, classify_risk


class PredictionService:
    """Tekil ve toplu churn tahminlerini ureten servis."""

    def __init__(
        self,
        model: Any,
        scaler: Any,
        expected_features: Optional[list[str]],
    ) -> None:
        """Tahmin servisini model bilesenleri ile baslatir.

        Args:
            model: predict ve predict_proba metotlarini destekleyen model.
            scaler: Modelin bekledigi olceklendirici nesne.
            expected_features: Model egitimindeki ozellik sirasi.
        """
        self.model = model
        self.scaler = scaler
        self.expected_features = expected_features or []

    def is_ready(self) -> bool:
        """Servisin tahmin yapmaya hazir olup olmadigini dondurur.

        Returns:
            bool: Model, scaler ve ozellikler mevcutsa True.
        """
        return self.model is not None and self.scaler is not None and bool(self.expected_features)

    def predict_one(self, customer_data: dict[str, Any]) -> dict[str, Any]:
        """Tek bir musteri icin churn tahmini uretir.

        Args:
            customer_data: Musteri ozelliklerini iceren sozluk.

        Returns:
            dict[str, Any]: Tahmin, olasilik ve risk seviyesi.
        """
        scaled_input = self._preprocess(pd.DataFrame([customer_data]))
        probability = float(self.model.predict_proba(scaled_input)[0][1])
        prediction = int(self.model.predict(scaled_input)[0])

        return {
            "churn_tahmini": prediction,
            "churn_ihtimali": probability,
            "risk_seviyesi": classify_risk(probability),
        }

    def predict_probabilities(self, customers: pd.DataFrame) -> np.ndarray:
        """Toplu musteri verisi icin churn olasiliklarini hesaplar.

        Args:
            customers: Tahmin edilecek musteri kayitlari.

        Returns:
            np.ndarray: Churn olasiliklari dizisi.
        """
        scaled_input = self._preprocess(customers)
        return self.model.predict_proba(scaled_input)[:, 1]

    def predict_batch(self, customers: list[dict[str, Any]]) -> dict[str, Any]:
        """Toplu musteri verisi icin tahmin ve ozet istatistik uretir.

        Args:
            customers: Musteri ozellik sozluklerinden olusan liste.

        Returns:
            dict[str, Any]: Sonuclar ve risk ozeti.
        """
        df_all = pd.DataFrame(customers)
        scaled_input = self._preprocess(df_all)
        probabilities = self.model.predict_proba(scaled_input)[:, 1]
        predictions = self.model.predict(scaled_input)

        results = [
            {
                "index": index,
                "churn_tahmini": int(prediction),
                "churn_ihtimali": round(float(probability), 4),
                "risk_seviyesi": classify_risk(float(probability)),
            }
            for index, (probability, prediction) in enumerate(zip(probabilities, predictions))
        ]

        total = len(results)
        high_risk = sum(
            1 for result in results if result["churn_ihtimali"] >= HIGH_RISK_THRESHOLD
        )
        medium_risk = sum(
            1
            for result in results
            if MEDIUM_RISK_THRESHOLD <= result["churn_ihtimali"] < HIGH_RISK_THRESHOLD
        )
        low_risk = total - high_risk - medium_risk
        average_risk = (
            sum(result["churn_ihtimali"] for result in results) / total if total else 0.0
        )

        return {
            "toplam_musteri": total,
            "ozet": {
                "yuksek_riskli": high_risk,
                "orta_riskli": medium_risk,
                "dusuk_riskli": low_risk,
                "ortalama_risk": round(average_risk, 4),
            },
            "sonuclar": results,
        }

    def _preprocess(self, customers: pd.DataFrame) -> np.ndarray:
        """Model oncesi ortak veri hazirligini calistirir.

        Args:
            customers: Ham musteri verisi.

        Returns:
            np.ndarray: Modelin bekledigi olceklenmis veri.
        """
        return preprocess_data(customers, self.expected_features, self.scaler)
