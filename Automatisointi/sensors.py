"""
sensors.py

Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.

Tämän moduulin tehtävä:
- Lukea sensoridataa eri lähteistä (Modbus, HTTP, tms.) 
- Kerätä yhteen data ja palauttaa SensorData-muodossa

Huom: sensori data on raakaa, ei suodatettua tai käsiteltyä
"""

from robot_types import SensorData
from robot_config import CAMERA_AVABLE, IMU_AVABLE, IO_AVABLE, MODBUS_AVAILABLE, DEBUG_SENSOR_VALUES
from modbus_worker import modbus_worker
import requests
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG_SENSOR_VALUES else logging.INFO)

# --- Kameran syvyysdatan luku ---
def read_camera_depth():
    if not CAMERA_AVABLE:
        return None, None, None
    try:
        # TODO: tee oikea luku
        r = requests.get("http://camera_container:8000/depth", timeout=0.05)
        data = r.json()
        return data["left"], data["center"], data["right"]
    except Exception as e:
        logger.error(f"Camera read failed: {e}")

        return None, None, None
# --- IMU-datan luku ---
def read_IMU_heading():
    if not IMU_AVABLE:
        return None, None, None
    return 0.0, 0.0, 0.0  # TODO: oikea IMU-luku

def safe_motor_freq(motor_id):
    if not MODBUS_AVAILABLE:
        return None
    data = modbus_worker.get_status(motor_id)
    logger.debug(f"Motor {motor_id} frequency: {data.get('frequency_Hz') if data else 'N/A'}")

    return data.get("frequency_Hz") if data else None

def safe_motor_voltage(motor_id: int) -> float | None:
    """Palauttaa moottorin jännitteen tai None, jos dataa ei ole saatavilla."""
    if not MODBUS_AVAILABLE:
        return None

    data = modbus_worker.get_status(motor_id)
    voltage = data.get("voltage_V") if data else None
    logger.debug(f"Motor {motor_id} voltage: {voltage if voltage is not None else 'N/A'}")
    return voltage

# --- IO-datan luku ---
def read_IO_data():
    if not IO_AVABLE:
        return 1, 0, 0, 0, 0
    return 0, 0, 0, 0, 0  # TODO: oikea IO-luku


def read_sensors() -> SensorData:
    motor1_freg = safe_motor_freq(1)
    motor3_freg = safe_motor_freq(3)
    motor4_freg = safe_motor_freq(4)
    motor6_freg = safe_motor_freq(6)

    battery1_voltage = safe_motor_voltage(1)
    battery2_voltage = safe_motor_voltage(4)

    cam_left, cam_center, cam_right = read_camera_depth() if CAMERA_AVABLE else (None, None, None)
    imu_x, imu_y, imu_z = read_IMU_heading() if IMU_AVABLE else (None, None, None)

    return SensorData(
        motor1_measured_freq=motor1_freg,
        motor3_measured_freq=motor3_freg,
        motor4_measured_freq=motor4_freg,
        motor6_measured_freq=motor6_freg,
        battery1_voltage=battery1_voltage,
        battery2_voltage=battery2_voltage,
        cam_measured_depth_left=cam_left,
        cam_measured_depth_center=cam_center,
        cam_measured_depth_right=cam_right,
        IMU_heading_x=imu_x,
        IMU_heading_y=imu_y,
        IMU_heading_z=imu_z,
        IO_data_1=read_IO_data()[0],
        IO_data_2=read_IO_data()[1],
        IO_data_3=read_IO_data()[2],
        IO_data_4=read_IO_data()[3],
        IO_data_5=read_IO_data()[4],
    )
