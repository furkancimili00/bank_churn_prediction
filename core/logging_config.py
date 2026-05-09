"""
Merkezi loglama yapılandırması.
Proje genelinde tutarlı, yapılandırılmış log çıktısı sağlar.
loguru kütüphanesi kullanılarak JSON formatında dosya ve konsol loglaması yapılır.
"""

import sys
from loguru import logger

# Varsayılan loguru sink'ini kaldır (stdout duplikasyonunu engellemek için)
logger.remove()

# Konsol çıktısı (renkli, okunabilir format)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    level="INFO",
    colorize=True,
)

# Dosya çıktısı (JSON formatında, rotasyonlu)
logger.add(
    "logs/churn_app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
)


def get_logger(module_name: str) -> "logger":
    """
    Modül bazlı logger döndürür.

    Args:
        module_name (str): Logger'ın bağlı olacağı modül adı.

    Returns:
        loguru.logger: Yapılandırılmış logger objesi.
    """
    return logger.bind(name=module_name)
