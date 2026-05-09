from fastapi import APIRouter, Depends
from api.dependencies import get_api_key

router = APIRouter(tags=["Sistem ve Yönetim"])

@router.get("/")
def health_check() -> dict[str, str]:
    """
    API'nin çalışıp çalışmadığını kontrol eden sağlık (health-check) bitiş noktası.
    """
    return {"status": "success", "message": "Churn Tahmin API aktif olarak çalışıyor."}


@router.get("/audit/logs", dependencies=[Depends(get_api_key)])
def get_audit_logs(limit: int = 50) -> dict[str, dict | list]:
    """
    Son denetim günlüğü kayıtlarını döner.
    """
    from services.audit_service import get_recent_events, get_event_summary

    events = get_recent_events(limit=limit)
    summary = get_event_summary()

    return {
        "ozet": summary,
        "kayitlar": events,
    }
