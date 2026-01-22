#!/usr/bin/env bash
set -e

echo "========================================"
echo " Kamera-simulaattorin käynnistys"
echo "========================================"

# --- Ympäristömuuttujat robottisovellukselle ---

export CAMERA_URL="http://localhost:8000/depth"
export IMU_URL="http://localhost:8000/IMU"
export IO_URL="http://localhost:8000/IO"
# Halutessasi:

export CAMERA_AVAILABLE=1
export IMU_AVAILABLE=1
export IO_AVAILABLE=1
# export MODBUS_AVAILABLE=0

echo "CAMERA_URL = $CAMERA_URL"

# --- Käynnistä simulaattori ---
echo ""
echo "Käynnistetään Docker Compose (kamera-simulaattori)..."
docker compose -f docker-compose-camera_depth_sim.yml up --build -d

echo ""
echo "Simulaattori käynnissä:"
docker ps --filter "name=simulator"

echo ""
echo "Testaa:"
echo "  curl http://localhost:8000/depth"
echo "  curl -X POST \"http://localhost:8000/set_depth?left=10&center=20&right=30\""
echo ""
echo "Käynnistä robotti hostissa:"
echo "jaskagui"
echo "Sammuta simulaattori hostissa:" 
echo "docker compose -f docker-compose-camera_depth_sim.yml down"
echo ""
