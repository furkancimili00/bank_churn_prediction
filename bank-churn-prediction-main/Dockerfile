FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem bağımlılıklarını kur (eğer gerekliyse, örneğin derleme araçları vs.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılık dosyasını kopyala
COPY requirements.txt /app/

# Python paketlerini kur
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Tüm kodları kopyala
COPY . /app/

# Eğer portlar tanımlanmak istenirse EXPOSE edilebilir (ancak docker-compose tarafında da verilecek)
EXPOSE 8000
EXPOSE 8501
