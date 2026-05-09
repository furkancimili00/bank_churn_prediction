"""Guvenlik dogrulama yardimcilari."""

from secrets import compare_digest
from typing import Optional


def is_valid_api_key(
    provided_key: Optional[str],
    configured_key: Optional[str],
) -> bool:
    """API anahtarini zamanlama saldirilarina karsi guvenli sekilde karsilastirir.

    Args:
        provided_key: Istek basligindan gelen API anahtari.
        configured_key: Sunucu tarafinda tanimli API anahtari.

    Returns:
        bool: Anahtarlar gecerli ve esitse True.
    """
    if not provided_key or not configured_key:
        return False

    return compare_digest(provided_key, configured_key)
