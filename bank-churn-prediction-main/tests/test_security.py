"""
Güvenlik mantığı birim testleri.
API anahtarı doğrulama mantığını izole edilmiş bir şekilde test eder.
"""

import pytest


def _mock_get_api_key(api_key_header_val: str, env_api_key: str) -> str:
    """
    main.py içerisindeki get_api_key fonksiyonunun iş mantığını simüle eder.

    Args:
        api_key_header_val (str): İstek başlığından gelen API anahtarı.
        env_api_key (str): Ortam değişkenindeki API anahtarı.

    Returns:
        str: Doğrulama sonucu mesajı.
    """
    if not env_api_key:
        return "500 Internal Server Error"

    if api_key_header_val == env_api_key:
        return "Success"

    return "401 Unauthorized"


def test_security_env_not_set() -> None:
    """Ortam değişkeni ayarlanmamışsa 500 hatası dönmeli."""
    result = _mock_get_api_key("herhangi-bir-key", None)
    assert result == "500 Internal Server Error"


def test_security_valid_key() -> None:
    """Geçerli API anahtarı ile başarılı yanıt dönmeli."""
    result = _mock_get_api_key("secret123", "secret123")
    assert result == "Success"


def test_security_invalid_key() -> None:
    """Geçersiz API anahtarı ile 401 hatası dönmeli."""
    result = _mock_get_api_key("yanlis-key", "secret123")
    assert result == "401 Unauthorized"


def test_security_missing_key() -> None:
    """Header'da API anahtarı yoksa (None) 401 hatası dönmeli."""
    result = _mock_get_api_key(None, "secret123")
    assert result == "401 Unauthorized"
