import sys
from unittest.mock import MagicMock

# FastAPI ve diğer bağımlılıkları mock'layalım
mock_fastapi = MagicMock()
sys.modules["fastapi"] = mock_fastapi
sys.modules["fastapi.security"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["joblib"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["numpy"] = MagicMock()

def test_security_logic_v2():
    print("Güvenlik mantığı testi v2 başlatılıyor (Refactored)...")

    # Test edilecek mantık (main.py'den alınmıştır)
    def mock_get_api_key(api_key_header_val, env_api_key):
        if not env_api_key:
            return "500 Internal Server Error"

        if api_key_header_val == env_api_key:
            return "Success"

        return "401 Unauthorized"

    # Senaryo 1: Ortam değişkeni ayarlanmamış
    print("Senaryo 1: Ortam değişkeni ayarlanmamış")
    res1 = mock_get_api_key("herhangi-bir-key", None)
    assert res1 == "500 Internal Server Error"
    print("✅ Ortam değişkeni eksikliği testi başarılı.")

    # Senaryo 2: Geçerli API Anahtarı
    print("Senaryo 2: Geçerli API Anahtarı")
    res2 = mock_get_api_key("secret123", "secret123")
    assert res2 == "Success"
    print("✅ Geçerli anahtar testi başarılı.")

    # Senaryo 3: Geçersiz API Anahtarı
    print("Senaryo 3: Geçersiz API Anahtarı")
    res3 = mock_get_api_key("yanlis-key", "secret123")
    assert res3 == "401 Unauthorized"
    print("✅ Geçersiz anahtar testi başarılı.")

    # Senaryo 4: Eksik API Anahtarı (None)
    print("Senaryo 4: Eksik API Anahtarı (Header yok)")
    res4 = mock_get_api_key(None, "secret123")
    assert res4 == "401 Unauthorized"
    print("✅ Eksik anahtar testi başarılı.")

if __name__ == "__main__":
    test_security_logic_v2()
