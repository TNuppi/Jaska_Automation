# state.py
from dataclasses import dataclass
from threading import Lock
from typing import Optional
from robot_types import PerceptionData
_tila = None
@dataclass
class RobotStateData:
    control_type: str = "AUTO"     # AUTO / MAN
    motion: str = "STOP"           # STOP, FORWARD, MAN FORWARD jne.
    last_motion: Optional[str] = None
    distance_travelled: float = 0.0
    start_distance: Optional[float] = None
    target_distance: Optional[float] = None

class RobotStateManager:
    """Singleton-tilan hallinta robotille."""
    def __init__(self):
        self._state = RobotStateData()
        self._perception: Optional[PerceptionData] = None
        self._lock = Lock()

    # ----------------- STATE -----------------
    def get_state(self) -> RobotStateData:
        with self._lock:
            return self._state

    def update_state(self, **kwargs):
        """Päivittää robotin tilaa thread-safe."""
        with self._lock:
            for k, v in kwargs.items():
                if hasattr(self._state, k):
                    setattr(self._state, k, v)

    # ----------------- PERCEPTION -----------------
    def get_perception(self) -> Optional[PerceptionData]:
        with self._lock:
            return self._perception

    def update_perception(self, perception: PerceptionData):
        with self._lock:
            self._perception = perception

    # ----------------- HELPERS -----------------
    def request_stop(self):
        with self._lock:
            self._state.last_motion = self._state.motion
            self._state.motion = "STOP"

    def get_distance_info(self):
        with self._lock:
            return self._state.start_distance, self._state.target_distance

    def add_distance_travelled(self, delta: float):
        with self._lock:
            self._state.distance_travelled += delta

def set_manual_mode():
    """Vaihda robotin tila MANUAL-moodiin."""
    robot_state.update_state(control_type="MAN", last_motion=robot_state.get_state().motion)
    
def set_auto_mode():
    """Vaihda robotin tila AUTO-moodiin."""
    robot_state.update_state(control_type="AUTO", last_motion=robot_state.get_state().motion)

# KRIITTINEN: Käytetään aina tätä samaa instanssia
robot_state = RobotStateManager()


