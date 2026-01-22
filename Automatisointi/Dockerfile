# Jetson Orin NX: käytä ARM64-yhteensopivaa Pythonia
FROM python:3.10-slim

# Estää Pythonia bufferoinnista (lokit näkyvät heti)
ENV PYTHONUNBUFFERED=1

# NiceGUI käyttää tätä
ENV NICEGUI_HOST=0.0.0.0
ENV NICEGUI_PORT=8080

WORKDIR /app

# --- Järjestelmäriippuvuudet ---
# minimalmodbus → pyserial → tarvitsee usein udev / serial-tukea
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    udev \
    && rm -rf /var/lib/apt/lists/*

# --- Python-riippuvuudet ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Sovelluskoodi ---
COPY . .

# --- NiceGUI portti ---
EXPOSE 8080

# --- Käynnistys ---
CMD ["python", "main.py"]
