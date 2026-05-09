import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.security import is_valid_api_key


def test_is_valid_api_key_accepts_matching_key() -> None:
    """Dogru API anahtari kabul edilmeli."""
    assert is_valid_api_key("secret-key", "secret-key") is True


def test_is_valid_api_key_rejects_missing_or_invalid_key() -> None:
    """Eksik veya hatali API anahtari reddedilmeli."""
    assert is_valid_api_key(None, "secret-key") is False
    assert is_valid_api_key("wrong-key", "secret-key") is False
    assert is_valid_api_key("secret-key", None) is False
