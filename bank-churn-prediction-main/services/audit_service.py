"""
Denetim Günlüğü (Audit Log) servis modülü.
Tahmin istekleri, oturum açma/kapama ve dosya yükleme gibi işlemlerin
zaman damgalı kaydını tutar.
"""

import json
import os
from datetime import datetime
from typing import Optional
from core.logging_config import get_logger

logger = get_logger(__name__)

AUDIT_LOG_FILE = os.path.join("logs", "audit_log.jsonl")


def _ensure_log_dir() -> None:
    """Log dizinini oluşturur (yoksa)."""
    os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)


def log_event(
    event_type: str,
    details: Optional[dict] = None,
    user: str = "system",
) -> dict:
    """
    Denetim olayını kayıt altına alır (JSONL formatında dosyaya yazar).

    Args:
        event_type (str): Olay tipi (ör. 'predict', 'login', 'upload', 'batch_predict').
        details (Optional[dict]): Ek olay detayları.
        user (str): İşlemi yapan kullanıcı.

    Returns:
        dict: Kaydedilen olay bilgisi.
    """
    _ensure_log_dir()

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "user": user,
        "details": details or {},
    }

    try:
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        logger.debug(f"Denetim kaydı: {event_type}")
    except Exception as e:
        logger.error(f"Denetim kaydı yazılamadı: {e}")

    return event


def get_recent_events(limit: int = 50) -> list[dict]:
    """
    En son denetim olaylarını döner.

    Args:
        limit (int): Döndürülecek maksimum olay sayısı.

    Returns:
        list[dict]: Son olaylar listesi (en yeniden en eskiye).
    """
    _ensure_log_dir()

    if not os.path.exists(AUDIT_LOG_FILE):
        return []

    events = []
    try:
        with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    except Exception as e:
        logger.error(f"Denetim kaydı okunamadı: {e}")
        return []

    # En yeniden en eskiye sırala ve limitle
    return events[-limit:][::-1]


def get_event_summary() -> dict:
    """
    Denetim loglarının özet istatistiklerini döner.

    Returns:
        dict: Olay tipi bazlı sayılar ve toplam kayıt.
    """
    events = get_recent_events(limit=10000)

    summary = {
        "toplam_kayit": len(events),
        "olay_tipleri": {},
    }

    for event in events:
        event_type = event.get("event_type", "bilinmiyor")
        summary["olay_tipleri"][event_type] = summary["olay_tipleri"].get(event_type, 0) + 1

    if events:
        summary["son_olay"] = events[0].get("timestamp", "—")
        summary["ilk_olay"] = events[-1].get("timestamp", "—")

    return summary


def clear_audit_log() -> bool:
    """
    Denetim logunu temizler (sıfırlar).

    Returns:
        bool: Başarılı ise True.
    """
    _ensure_log_dir()
    try:
        with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
        logger.info("Denetim logu temizlendi")
        return True
    except Exception as e:
        logger.error(f"Denetim logu temizlenemedi: {e}")
        return False
