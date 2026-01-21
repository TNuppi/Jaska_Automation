"""
perception.py

Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.

Tämän moduulin tehtävä:
- Muuntaa SensorData korkeamman tason havainnoiksi
- Laskea robotin liike- ja ympäristöhavainnot
- Palauttaa PerceptionData-muodossa

HUOM:
- Ei päätöksentekoa
- Ei moottoriohjausta
"""

from robot_types import SensorData, PerceptionData
from robot_config import (
    WHEEL_DIAMETER,
    OBSTACLE_MIN_DISTANCE,
    OBSTACLE_NEAR_DISTANCE,
    RPM_FACTOR,
    DEBUG_PERCEPTION
)
import math
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG_PERCEPTION else logging.INFO)

# ---------- PÄÄRAJAPINTA ----------

def perceive(sensor_data: SensorData) -> PerceptionData:
    """
    Muuntaa SensorData-olion PerceptionData-olioksi.
    """
    rpms = calculate_motor_rpms(sensor_data)
    logger.debug(f"Motor RPMs: {rpms}")
    velocity = calculate_linear_velocity(rpms)
    logger.debug(f"Calculated linear velocity: {velocity} m/s")
    heading = calculate_heading(sensor_data)
    logger.debug(f"Calculated heading: {heading} rad")
    obstacle_front, obstacle_near = detect_obstacles(sensor_data)
    logger.debug(f"Obstacle front: {obstacle_front}, Obstacle near: {obstacle_near}")
    battery1 = sensor_data.battery1_voltage
    battery2 = sensor_data.battery2_voltage
    logger.debug(f"Battery1 voltage: {battery1} V, Battery2 voltage: {battery2} V")
    io_data = read_IO_states(sensor_data)


    perception = PerceptionData(
        obstacle_near=obstacle_near,
        obstacle_front=obstacle_front,
        heading=heading,
        measured_velocity=velocity,
        emmergency_stop=io_data["emmergency_stop"],
        reset_button=io_data["reset_button"],
        battery1=battery1,
        battery2=battery2
    )
    
    return perception


# ---------- ALIFUNKTIOT ----------

# --- Moottorien kierrosnopeudet (RPM) ---

def calculate_motor_rpms(sensor_data: SensorData) -> dict:
    motor_freqs = [
        sensor_data.motor1_measured_freq,
        sensor_data.motor3_measured_freq,
        sensor_data.motor4_measured_freq,
        sensor_data.motor6_measured_freq
    ]
    motor_names = ["motor1", "motor3", "motor4", "motor6"]
    
    motor_rpms = {}
    for name, freq in zip(motor_names, motor_freqs):
        if freq is None:
            logger.warning(f"{name} frequency is None -> using 0 RPM")
            freq = 0.0
        motor_rpms[name] = freq * RPM_FACTOR

    return motor_rpms


# --- Lineaarinen nopeus ---

def calculate_linear_velocity(motor_rpms: dict[str,float]) -> float:
    """
    Laskee robotin lineaarisen nopeuden (m/s)
    moottorien kierrosnopeuksista (RPM).
    """
    # TODO: toteuta
    if not motor_rpms:
        return 0.0
    rpms = list(motor_rpms.values())
    avg_rpm = sum(rpms) /len(rpms) # taajuuksien keskiarvo
    velocity = avg_rpm *math.pi*WHEEL_DIAMETER/60

    return velocity




def calculate_heading(sensor_data: SensorData) -> float:
    """
    Laskee robotin suuntiman IMU-datasta.
    """
    # TODO: esim. käytä z-akselia
    return sensor_data.IMU_heading_z

def detect_obstacles(sensor_data) -> tuple[bool, bool]:
    """
    Päättelee estehavainnot kameran syvyystiedoista.

    Kamera:
    - inf  = ei estettä
    - nan  = este liian lähellä -> VAARA
    - float = mitattu etäisyys milleinä
    - None = dataa ei saatavilla -> VAARA
    """

    depths = {
        "left": sensor_data.cam_measured_depth_left,
        "center": sensor_data.cam_measured_depth_center,
        "right": sensor_data.cam_measured_depth_right,
    }

    obstacle_front = False
    obstacle_near = False

    for position, d in depths.items():

        # --- None = dataa ei saatavilla ---
        if d is None:
            logger.error(f"Obstacle DATA MISSING ({position})")
            obstacle_front = True
            obstacle_near = True
            continue
        # --- NaN = este liian lähellä ---
        if math.isnan(d):
            logger.warning(f"Obstacle TOO CLOSE ({position})")
            obstacle_front = True
            obstacle_near = True
            continue

        # --- inf = ei estettä ---
        if d is None or math.isinf(d):
            continue

        # --- Normaali etäisyys ---
        if d < OBSTACLE_MIN_DISTANCE:
            obstacle_front = True

        if d < OBSTACLE_NEAR_DISTANCE:
            obstacle_near = True

    return obstacle_front, obstacle_near

# --- IO käsittely ---
def read_IO_states(sensor_data: SensorData) -> dict[str, int]:
    """
    Lukee IO-dataa SensorData-oliosta.
    """
    emmergency_stop = False if sensor_data.IO_data_1 == 1 else True
    reset_button = True if sensor_data.IO_data_2 == 1 else False
    return {
        "emmergency_stop": emmergency_stop,
        "reset_button": reset_button,
    }

# --- TESTAUSKODI ---
if __name__ == "__main__":
    from sensors import read_sensors
    sensors = read_sensors()
    perception = perceive(sensors)
    motor_rpms = calculate_motor_rpms(sensors)
    print("Perception:", perception)
    print("Motor RPMs:", motor_rpms)
