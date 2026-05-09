"""Uygulama ayarlarini merkezi olarak yoneten modul."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORS_ORIGINS = "http://localhost:8501,http://127.0.0.1:8501"


@dataclass(frozen=True)
class Settings:
    """Ortam degiskenlerinden okunan uygulama ayarlari."""

    api_key: Optional[str]
    cors_origins: list[str]
    model_path: Path
    api_version: str = "2.0.0"

    @classmethod
    def from_env(cls) -> "Settings":
        """Ortam degiskenlerini okuyarak ayar nesnesi olusturur.

        Returns:
            Settings: API, CORS ve model yolu ayarlarini tasiyan nesne.
        """
        cors_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
            if origin.strip()
        ]
        model_path = Path(os.getenv("CHURN_MODEL_PATH", "churn_thesis_model.skops"))
        if not model_path.is_absolute():
            model_path = PROJECT_ROOT / model_path

        return cls(
            api_key=os.getenv("CHURN_API_KEY"),
            cors_origins=cors_origins,
            model_path=model_path,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Uygulama ayarlarini onbellekten dondurur.

    Returns:
        Settings: Merkezi uygulama ayarlari.
    """
    return Settings.from_env()
