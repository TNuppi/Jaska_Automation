# sensors.py
from robot_types import SensorData
from robot_config import CAMERA_AVABLE, IMU_AVABLE, USE_SIMULATION, MODBUS_AVAILABLE
from modbus_worker import modbus_worker
import random
import requests
import logging

logger = logging.getLogger(__name__)

def read_camera_depth():
    if not CAMERA_AVABLE:
        return None, None, None
    try:
        r = requests.get("http://camera_container:8000/depth", timeout=0.05)
        data = r.json()
        return data["left"], data["center"], data["right"]
    except Exception as e:
        logger.error(f"Camera read failed: {e}")
        return None, None, None

def read_IMU_heading():
    if not IMU_AVABLE:
        return None, None, None
    return 0.0, 0.0, 0.0  # TODO: oikea IMU-luku

def safe_motor_freq(motor_id):
    if not MODBUS_AVAILABLE:
        return None
    data = modbus_worker.get_status(motor_id)
    return data.get("frequency_Hz") if data else None

def read_sensors() -> SensorData:
    motor1 = safe_motor_freq(1)
    motor3 = safe_motor_freq(3)
    motor4 = safe_motor_freq(4)
    motor6 = safe_motor_freq(6)

    cam_left, cam_center, cam_right = read_camera_depth() if CAMERA_AVABLE else (None, None, None)
    imu_x, imu_y, imu_z = read_IMU_heading() if IMU_AVABLE else (None, None, None)

    return SensorData(
        motor1_measured_freq=motor1,
        motor3_measured_freq=motor3,
        motor4_measured_freq=motor4,
        motor6_measured_freq=motor6,
        cam_measured_depth_left=cam_left,
        cam_measured_depth_center=cam_center,
        cam_measured_depth_right=cam_right,
        IMU_heading_x=imu_x,
        IMU_heading_y=imu_y,
        IMU_heading_z=imu_z,
    )
