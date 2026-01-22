"""
state.py

Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.

Tämän moduulin tehtävä:
- Hallita robotin tilaa (state)
- Pysyvät muuttujat (esim. kuljettu matka, viimeisin havainto)
"""
from dataclasses import dataclass
from threading import Lock
from typing import Optional
from robot_types import PerceptionData
import logging
import time

_last_time = None
logger = logging.getLogger(__name__)

# ----------------- DATA -----------------

@dataclass
class RobotStateData:
    status: str = "OK"
    last_status: Optional[str] = None
    error_source: Optional[str] = None
    control_type: str = "AUTO"
    motion: str = "STOP"
    last_motion: Optional[str] = None
    last_turn: Optional[str] = None

    prev_reset_button: bool = False
    
    distance_travelled: float = 0.0
    start_distance: float = 0.0
    target_distance: float = 0.0
    perception: Optional[PerceptionData] = None

# ----------------- MODUULI-TILA (SINGLETON) -----------------

_state = RobotStateData()

_lock = Lock()


# ----------------- STATE FUNKTIOT -----------------

def get_state() -> RobotStateData:
    """Palauttaa KOPION robotin tilasta (thread-safe).
    status: str # esim. "OK" "ERROR" 
    control_type: str # MAN |AUTO
    motion: str # esim. "STOP", "FORWARD", "TURNING_LEFT"
    last_motion: str | None #edellinen tila 
    last_turn: str | None  esim. "LEFT", "RIGHT" tai None
    
    prev_reset_button: bool  # edellinen reset nappi tila

    distance_travelled: float # kuljettu matka
    target_distance: float | None
    start_distance: float | None 
    
    """
    with _lock:
        return RobotStateData(**vars(_state))


def update_state(**kwargs):
    """Päivittää robotin tilaa thread-safe.
    status: str # esim. "OK" "ERROR" 
    control_type: str # MAN |AUTO
    motion: str # esim. "STOP", "FORWARD", "TURNING_LEFT"
    last_motion: str | None #edellinen tila 
    last_turn: str | None  esim. "LEFT", "RIGHT" tai None
    
    prev_reset_button: bool  # edellinen reset nappi tila

    distance_travelled: float # kuljettu matka
    target_distance: float | None
    start_distance: float | None 
    
    """
    with _lock:
        for k, v in kwargs.items():
            if hasattr(_state, k):
                setattr(_state, k, v)


# ----------------- PERCEPTION -----------------

def get_perception() -> Optional[PerceptionData]:
    """
    palauttaa perception datan
    obstacle_near: bool # Este lähellä
    obstacle_front: bool # Este edessä
    heading: float # Suuntima
    measured_velocity: float # sensoridatasta lakettu
    battery1: float | None # Akun 1 jännite
    battery2: float | None # Akun 2 jännite
    emmergency_stop: bool # Hätä seis tila
    reset_button: bool # Reset nappi painettu
    """
    with _lock:
        return _state.perception


def update_perception(perception: PerceptionData):
    """
    päivittää perceptiondatan
    obstacle_near: bool # Este lähellä
    obstacle_front: bool # Este edessä
    heading: float # Suuntima
    measured_velocity: float # sensoridatasta lakettu
    battery1: float | None # Akun 1 jännite
    battery2: float | None # Akun 2 jännite
    emmergency_stop: bool # Hätä seis tila
    reset_button: bool # Reset nappi painettu
    """

    with _lock:
        _state.perception = perception


# ----------------- MODE HELPERS -----------------

def set_manual_mode():
    """Vaihda MAN-tilaan."""
    with _lock:
        _state.last_motion = _state.motion
        _state.control_type = "MAN"


def set_auto_mode():
    """Vaihda AUTO-tilaan."""
    with _lock:
        _state.last_motion = _state.motion
        _state.control_type = "AUTO"


def request_stop():
    """Pysäytä liike säilyttäen last_motion."""
    with _lock:
        _state.last_motion = _state.motion
        _state.motion = "STOP"


# ----------------- DISTANCE HELPERS -----------------

def get_distance_info():
    """
    palauttaa matkat start, target, tarvelled
    """
    with _lock:
        return _state.start_distance, _state.target_distance, _state.distance_travelled


def add_distance_travelled(distance: float):
    with _lock:
        _state.distance_travelled += distance

def reset_distance_travelled():
    """Nollaa kuljetun matkan. ja viime aijan"""
    global _last_time
    with _lock:
        
        _state.distance_travelled = 0.0
        _last_time = None

def calculate_time_delta() -> float:
    """Laskee kuluneen ajan edellisestä kutsusta sekunteina."""
    global _last_time
    now = time.monotonic()
    if _last_time is None:
        _last_time = now
        return 0.0
    delta = now - _last_time
    _last_time = now
       # turvaraja esim. GUI freeze / breakpoint
    return min(delta, 0.5)


