import subprocess
import sys
import time
import os
from core.logging_config import get_logger

logger = get_logger(__name__)

def start_services() -> None:
    """
    FastAPI backend ve Streamlit frontend servislerini paralel olarak başlatır.

    FastAPI sunucusu 8000 portunda, Streamlit arayüzü 8501 portunda çalıştırılır.
    CTRL+C ile tüm servisler güvenli şekilde durdurulur.
    """
    logger.info("Banka Churn Projesi Başlatılıyor...")
    logger.info("=======================================")
    
    # 1. FastAPI Sunucusunu Başlatma
    logger.info("FastAPI (Backend API) başlatılıyor... (Port: 8000)")
    # Ortam değişkenine API KEY ekleyelim ki API güvenli modda çalışabilsin
    env = os.environ.copy()
    if "CHURN_API_KEY" not in env:
        env["CHURN_API_KEY"] = "admin_super_secret_key"
        
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        env=env
    )
    
    # Backend'in ayağa kalkması için kısa bir süre bekle
    time.sleep(3)
    logger.success("FastAPI başarıyla başlatıldı: http://127.0.0.1:8000")
    logger.info("API Dokümantasyonu (Swagger): http://127.0.0.1:8000/docs")
    
    # 2. Streamlit Arayüzünü Başlatma
    logger.info("Streamlit (Frontend Dashboard) başlatılıyor...")
    ui_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "dashboard.py"]
    )
    
    logger.success("TÜM SİSTEM AKTİF!")
    logger.info("Uygulamayı kapatmak için terminalde CTRL+C tuşlarına basabilirsiniz.")
    
    try:
        # Süreçleri beklet ki script hemen kapanmasın
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        logger.warning("Kapatma komutu alındı. Servisler durduruluyor...")
        api_process.terminate()
        ui_process.terminate()
        api_process.wait()
        ui_process.wait()
        logger.success("Tüm servisler başarıyla durduruldu.")

if __name__ == "__main__":
    start_services()
