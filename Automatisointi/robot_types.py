"""
robot_types.py

Luonut Tero Nikkola yhessä ChatGPT-5 mini:n kanssa.

Ohjelman tarkoituksena on määritellä koko ohjelmasssa käytettävät yhtenäisest tietotyypit ja niiden rakenteet.
Varmistaa, että moduulit käyttävät yhtenäisiä datamuotoja.

"""
from dataclasses import dataclass

# Sensoreilta saadut tiedot
@dataclass(frozen=True) # määritellään että data tyyppi on muuttumaton
class SensorData:
    motor1_measured_freq: float | None # Etu Paarpuuri
    motor3_measured_freq: float | None # Taka Paarpuuri 
    motor4_measured_freq: float | None # Etu Styyrpuuri
    motor6_measured_freq: float | None # Taka Styyrpuuri

    battery1_voltage: float | None  # Akun 1 jännite
    battery2_voltage: float | None  # Akun 2 jännite 

    cam_measured_depth_left: float | None  # kameran mittaama etäisyys vasen
    cam_measured_depth_center: float | None # kameran mittaama etäisyys keskellä
    cam_measured_depth_right: float | None # kameran mittaama etäisyys oikea
    
    IMU_heading_x: float # imun suuntima x akselin mukaan
    IMU_heading_y: float # imu suuntima y askelin mukaan
    IMU_heading_z: float # imu suuntima z akselin mukaan
    
    IO_data_1: int  # TODO: Lisää dataa
    IO_data_2: int
    IO_data_3: int
    IO_data_4: int
    IO_data_5: int
    
    # TODO: Lisää dataa

# Data tyypit PreceptionDatasta
@dataclass(frozen=True)
class PerceptionData:
    obstacle_near: bool # Este lähellä
    obstacle_front: bool # Este edessä
    heading: float # Suuntima
    measured_velocity: float # sensoridatasta lakettu
    battery1: float | None # Akun 1 jännite
    battery2: float | None # Akun 2 jännite
    emmergency_stop: bool # Hätä seis tila
    reset_button: bool # Reset nappi painettu
    # TODO: lisää mahdollisia juttuja

@dataclass(frozen=True)
class ControlCommand:
    linear_speed: float # m/s
    angular_speed: float # rad/s
    # TODO: tarviiko lisää?

@dataclass(frozen=True)
class RobotStateData:
    status: str # esim. ok, error
    control_type: str # MAN |AUTO
    motion: str # esim. "STOP", "FORWARD", "TURNING_LEFT"
    last_motion: str | None = None #edellinen tila 
    last_turn: str | None = None # "LEFT", "RIGHT" tai None
    
    prev_reset_button: bool = False # edellinen reset nappi tila

    distance_travelled: float = 0.0 # kuljettu matka
    target_distance: float | None = None
    start_distance: float | None = None
    # TODO: Mahdollisesti lisää tiloja

@dataclass(frozen=True)
class GUICommand:
    control_type: str # esim. "SET_MODE", "SET_MOTION"
    motion_type: str | None = None # esim. "FORWARD", "STOP"
    distance_value: float | None = None # esim. etäisyys tai nopeus