"""Churn risk siniflandirma kurallari."""

HIGH_RISK_THRESHOLD = 0.70
MEDIUM_RISK_THRESHOLD = 0.40


def classify_risk(probability: float) -> str:
    """Churn olasiligina gore okunabilir risk seviyesini belirler.

    Args:
        probability: Modelin urettigi churn olasiligi.

    Returns:
        str: Kullaniciya gosterilecek risk seviyesi mesaji.
    """
    if probability >= HIGH_RISK_THRESHOLD:
        return "Çok Yüksek Riskli - Acil İletişime Geçilmeli"
    if probability >= MEDIUM_RISK_THRESHOLD:
        return "Orta Riskli - Kampanya Önerilebilir"

    return "Düşük Riskli - Sadık Müşteri"
