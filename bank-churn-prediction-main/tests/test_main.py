import sys
import os

# Üst dizindeki modülleri içe aktarabilmek için sys.path güncelleniyor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check() -> None:
    """
    Health check (/) endpoint'inin doğru çalışıp çalışmadığını test eder.

    Beklenen Davranış:
        - 200 OK HTTP durum kodu döndürmelidir.
        - JSON yanıtında status 'success' ve API'nin aktif olduğunu belirten bir mesaj yer almalıdır.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Churn Tahmin API aktif olarak çalışıyor."}
