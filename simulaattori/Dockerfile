FROM python:3.10-slim

# Ei bufferointia → logit näkyvät heti
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Riippuvuudet
RUN pip install --no-cache-dir fastapi uvicorn

# Sovelluskoodi
COPY simulator.py .

# API-portti
EXPOSE 8000

# Käynnistys
CMD ["uvicorn", "simulator:app", "--host", "0.0.0.0", "--port", "8000"]
