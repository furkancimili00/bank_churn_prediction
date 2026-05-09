# Aşama 1: Bağımlılıkların derlenmesi (Builder)
FROM python:3.12-slim AS builder

WORKDIR /app

# Sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılık dosyasını kopyala ve wheel'ları oluştur
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Aşama 2: Çalışma zamanı ortamı (Runtime)
FROM python:3.12-slim

# Metadata etiketleri
LABEL maintainer="Bank Churn Team"
LABEL description="Banka Müşteri Churn Tahmin API ve Dashboard"
LABEL version="2.0.0"

WORKDIR /app

# Non-root kullanıcı oluştur (güvenlik)
RUN useradd -m -r -s /bin/false appuser

# Healthcheck için curl kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Wheel'ları builder'dan kopyala ve kur
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Log dizinini oluştur
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# Kodları kopyala ve izinleri ayarla
COPY --chown=appuser:appuser . /app/

# Kullanıcıyı değiştir
USER appuser

# Port'ları tanımla
EXPOSE 8000
EXPOSE 8501

# Sağlık kontrolü
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Varsayılan olarak FastAPI sunucusunu başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
