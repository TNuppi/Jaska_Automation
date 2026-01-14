# modbus_worker.py
import logging
import threading
import time
from robot_config import MOTOR_IDS
from ModbusDriver import modbus


logger = logging.getLogger(__name__)

class ModbusWorker(threading.Thread):
    def __init__(self, poll_interval=0.1):
        super().__init__(daemon=True)
        self.poll_interval = poll_interval
        self.running = False
        self.motor_status = {mid: {"frequency_Hz": 0} for mid in MOTOR_IDS}
        self.lock = threading.Lock()

    def run(self):
        self.running = True
        while self.running:
            for mid in MOTOR_IDS:
                # TODO: lue oikea Modbus täältä
                with self.lock:
                    data = modbus.read_status(mid)
                    if data:
                        self.motor_status[mid] = data
                    
            time.sleep(self.poll_interval)

    def stop(self):
        self.running = False

    def get_status(self, motor_id):
        with self.lock:
            return self.motor_status.get(motor_id, None)

    def set_speed(self, motor_id, speed):
        logger.debug(f"Setting motor {motor_id} speed to {speed}")
        modbus.set_speed(motor_id, speed)

    def set_direction(self, motor_id, direction):
        modbus.set_direction(motor_id, direction)
        logger.debug(f"Motor {motor_id}: direction set to {direction}")
    def emergency_stop(self):
        logger.info("Executing emergency stop on all motors")
        modbus.emergency_stop()
            
modbus_worker = ModbusWorker()
