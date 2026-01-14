# modbus_worker.py
import threading
import time
from robot_config import MOTOR_IDS

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
                    self.motor_status[mid]["frequency_Hz"] = 0
            time.sleep(self.poll_interval)

    def stop(self):
        self.running = False

    def get_status(self, motor_id):
        with self.lock:
            return self.motor_status.get(motor_id, None)

    def set_speed(self, motor_id, speed):
        print(f"Motor {motor_id}: speed set to {speed}")

    def set_direction(self, motor_id, direction):
        print(f"Motor {motor_id}: direction set to {direction}")

    def emergency_stop(self):
        self.set_direction(0, 0)
        self.set_speed(0, 0)
        

modbus_worker = ModbusWorker()
