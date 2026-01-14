# main.py
import threading
import time
import logging
import os
import signal

from sensors import read_sensors
from perception import perceive
from decision import decide
from control import apply_control, emergency_stop
from gui import start_gui
from robot_config import CONTROL_LOOP_DT

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("MAIN")

stop_event = threading.Event()


def is_nicegui_reload_process() -> bool:
    return os.environ.get("NICEGUI_PROCESS") == "reload"


def control_loop():
    logger.info("Control loop started")

    while not stop_event.is_set():
        try:
            sensors = read_sensors()
            perception = perceive(sensors)
            command = decide(perception)

            if command is not None:
                apply_control(command)
            else:
                emergency_stop()

        except Exception:
            logger.exception("CONTROL LOOP ERROR")
            emergency_stop()

        time.sleep(CONTROL_LOOP_DT)

    emergency_stop()
    logger.info("Control loop stopped")


def shutdown_handler(signum, frame):
    logger.info(f"Shutdown signal {signum} received")
    stop_event.set()


def main():
    logger.info(f"NICEGUI_PROCESS={os.environ.get('NICEGUI_PROCESS')}")

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if is_nicegui_reload_process():
        logger.info("NiceGUI reload/helper process – control loop NOT started")
    else:
        logger.info("Starting control loop thread")
        threading.Thread(target=control_loop, daemon=True).start()

    logger.info("Starting GUI")
    start_gui()  # 🔥 EI finally-lohkoa


if __name__ in {"__main__", "__mp_main__"}:
    main()
