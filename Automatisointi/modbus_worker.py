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
        self.commands = []  # komento-jonot (set_speed / set_direction)

    def run(self):
        self.running = True
        while self.running:
            with self.lock:
                # suorita kaikki jonossa olevat komennot ensin
                while self.commands:
                    cmd, motor_id, value = self.commands.pop(0)
                    if cmd == "set_speed":
                        modbus.set_speed(motor_id, value)
                        logger.debug(f"Motor {motor_id}: speed set to {value}")
                    elif cmd == "set_direction":
                        modbus.set_direction(motor_id, value)
                        logger.debug(f"Motor {motor_id}: direction set to {value}")
                
                # lue status
                for mid in MOTOR_IDS:
                    data = modbus.read_status(mid)
                    if data:
                        self.motor_status[mid] = data
            time.sleep(self.poll_interval)

    def stop_all(self):
        self.running = False
        modbus.set_direction(0, 0)  # pysäytä kaikki
        modbus.set_speed(0, 0)
        logger.info("All motors stopped")

    def get_status(self, motor_id):
        with self.lock:
            return self.motor_status.get(motor_id, None)

    def enqueue_set_speed(self, motor_id, speed):
        with self.lock:
            self.commands.append(("set_speed", motor_id, speed))

    def enqueue_set_direction(self, motor_id, direction):
        with self.lock:
            self.commands.append(("set_direction", motor_id, direction))

    def emergency_stop(self):
        logger.info("Executing emergency stop on all motors")
        modbus.emergency_stop()


# luo singleton-instanssi
modbus_worker = ModbusWorker()
