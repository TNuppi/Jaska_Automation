import threading
import time
import logging
from sensors import read_sensors
from perception import perceive
from decision import decide
from control import apply_control, emergency_stop
from gui import start_gui
from state import robot_state
from robot_config import CONTROL_LOOP_DT

# ----------------- LOGGING -----------------
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("MAIN")

# ----------------- STOP EVENT -----------------
stop_event = threading.Event()

# ----------------- CONTROL LOOP -----------------
def control_loop():
    """Kontrollisilmukka pyörii taustalla taustasäikeessä."""
    logger.info("Control loop started")
    while not stop_event.is_set():
        try:
            # 1) Lue sensorit
            sensors = read_sensors()

            # 2) Tee havainnointi
            perception = perceive(sensors)
            
            # 3) Päätöksenteko (decide käyttää suoraan robot_statea)
            command = decide(perception)

            # 4) Lähetä komento robotille
            if command is not None:
                apply_control(command)
            else:
                apply_control(robot_state.get_state().motion)  # fallback

        except Exception:
            logger.exception("CONTROL LOOP ERROR, executing emergency stop")
            emergency_stop()
            # Jatketaan loopia, ettei MAN/AUTO pysy jumissa

        # Odota seuraavaan silmukkaan
        time.sleep(CONTROL_LOOP_DT)

    # Kun loop loppuu, pysäytä robotti
    emergency_stop()
    logger.info("Control loop stopped")

# ----------------- MAIN -----------------
def main():
    # Käynnistä kontrollisilmukka taustasäikeessä
    threading.Thread(target=control_loop, daemon=True).start()
    logger.info("GUI starting...")

    # Käynnistä GUI pääsäikeessä
    try:
        start_gui()
    finally:
        logger.info("GUI closed, stopping control loop")
        stop_event.set()
        time.sleep(CONTROL_LOOP_DT * 2)

if __name__ in {"__main__", "__mp_main__"}:
    main()
