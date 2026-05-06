# Aşama 1: Bağımlılıkların derlenmesi ve kurulması (Builder)
FROM python:3.9-slim AS builder

WORKDIR /app

# Sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılık dosyasını kopyala
COPY requirements.txt .

# Bağımlılıkları geçici bir dizine kur
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Aşama 2: Çalışma zamanı ortamı (Runtime)
FROM python:3.9-slim

WORKDIR /app

# Non-root kullanıcı oluştur
RUN useradd -m -r appuser

# Healthcheck için curl kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Wheel'ları builder'dan kopyala ve kur
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Kodları kopyala ve izinleri ayarla
COPY --chown=appuser:appuser . /app/

# Kullanıcıyı değiştir
USER appuser

EXPOSE 8000
EXPOSE 8501
