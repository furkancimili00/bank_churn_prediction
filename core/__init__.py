"""
Core modülü — Projenin temel altyapı bileşenleri.
Loglama yapılandırması ve veri ön işleme yardımcılarını içerir.
"""

from core.logging_config import get_logger
from core.utils import preprocess_data

__all__ = ["get_logger", "preprocess_data"]
