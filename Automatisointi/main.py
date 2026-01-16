# main.py
import threading
import time
import logging
import os
import signal

from sensors import read_sensors
from perception import perceive
from decision import decide
from control import apply_control, stop_all_motors
from gui import start_gui
from robot_config import CONTROL_LOOP_DT, DEBUG_MAIN
from modbus_worker import modbus_worker
from state import update_perception, calculate_time_delta, add_distance_travelled

logging.basicConfig(
    
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("MAIN")
logger.setLevel(logging.DEBUG if DEBUG_MAIN else logging.INFO)
stop_event = threading.Event()


def is_nicegui_reload_process() -> bool:
    return os.environ.get("NICEGUI_PROCESS") == "reload"


def control_loop():
    logger.info("Control loop started")

    while not stop_event.is_set():
        try:
            # 1. Lue sensorit
            sensors = read_sensors()
            # 2. käsittele sensori data ja tee havainnointi
            perception = perceive(sensors)
            # 3. päivitä havainnointi tila
            update_perception(perception)
            # 4. laske kulunut aika
            dt = calculate_time_delta()
            # 5. laske kuljettu matka
            velocity = perception.measured_velocity or 0.0
            distance = dt * velocity
            add_distance_travelled(distance)
            # 6. tee päätös
            command = decide(perception)
            # 7. lähetä käsky moottoreille
            apply_control(command)

        except Exception:
            logger.exception("CONTROL LOOP ERROR")
            stop_all_motors()

        time.sleep(CONTROL_LOOP_DT)

    stop_all_motors()
    logger.info("Control loop stopped")


def shutdown_handler(signum, frame):
    logger.info(f"Shutdown signal {signum} received")
    stop_event.set()


def main():
    nicegui_process = os.environ.get("NICEGUI_PROCESS")
    logger.info(f"NICEGUI_PROCESS={nicegui_process}")

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if is_nicegui_reload_process():
        logger.info("NiceGUI reload/helper process – NO hardware threads started")
    else:
        logger.info("Starting control loop thread")
        threading.Thread(target=control_loop, daemon=True).start()

        logger.info("Starting Modbus worker thread")
        modbus_worker.start()

    logger.info("Starting GUI")
    start_gui()   # ui.run() BLOKKAA TÄSSÄ


if __name__ in {"__main__", "__mp_main__"}:
    main()
