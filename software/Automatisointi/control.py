"""
control.py

Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.
Tämän moduulin tehtävä:
- Lähettää ControlCommand moottoreille
- Muuntaa lineaariset ja kulmanopeudet moottorikohtaisiksi käskyiksi

"""
from robot_types import ControlCommand
from robot_config import (
    MAX_SPEED_VALUE,
    MAX_LINEAR_SPEED,
    MAX_ANGULAR_SPEED,
    MODBUS_AVAILABLE,
    PORTSIDE_MOTORS,
    STARBOAD_MOTORS,
)
from modbus_worker import modbus_worker
import logging


logger = logging.getLogger(__name__)

_last_command: ControlCommand | None = None  # viimeisin lähetetty käsky


def apply_control(command: ControlCommand | None):
    """
    Lähettää ControlCommandin moottoreille.
    Lähettää käskyn vain, jos se eroaa viimeisestä.
    """
    global _last_command

    if command is None:
        logger.debug("apply_control: command is None -> all motors stop")
        modbus_worker.stop_all()
        _last_command = None
        return

    # Sama käsky kuin viimeksi -> ei tehdä mitään
    if _last_command == command:
        return

    _last_command = command

    # Rajataan nopeudet turvalliselle alueelle
    linear = max(min(command.linear_speed, MAX_LINEAR_SPEED), -MAX_LINEAR_SPEED)
    angular = max(min(command.angular_speed, MAX_ANGULAR_SPEED), -MAX_ANGULAR_SPEED)

    motor_speeds = calculate_motor_speeds(linear, angular)
    send_to_motors(motor_speeds)


def calculate_motor_speeds(linear: float, angular: float) -> dict[int, int]:
    """
    Muuntaa lineaarisen ja kulmanopeuden moottorikohtaisiksi nopeuksiksi.
    """
    linear_norm = linear / MAX_LINEAR_SPEED if MAX_LINEAR_SPEED else 0.0
    angular_norm = angular / MAX_ANGULAR_SPEED if MAX_ANGULAR_SPEED else 0.0

    return {
        1: int((linear_norm - angular_norm) * MAX_SPEED_VALUE),
        3: int((linear_norm - angular_norm) * MAX_SPEED_VALUE),
        4: int((linear_norm + angular_norm) * MAX_SPEED_VALUE),
        6: int((linear_norm + angular_norm) * MAX_SPEED_VALUE),
    }


def send_to_motors(motor_vals: dict[int, int]):
    """
    Lähettää moottorikomentojen arvot joko Modbusin kautta tai simulointina.
    """
    try:
        for motor_id, signed_speed in motor_vals.items():
            direction, speed = speed_to_direction(motor_id, signed_speed)

            if MODBUS_AVAILABLE:
                modbus_worker.enqueue_set_direction(motor_id, direction)
                modbus_worker.enqueue_set_speed(motor_id, speed)
            else:
                logger.info(
                    f"[SIM] Motor {motor_id}: speed={speed}, direction={direction}"
                )
    except Exception:
        logger.exception("Failed to send motor commands")


def speed_to_direction(motor_id:int, speed: int) -> tuple[int, int]:
    """
    Muuntaa etumerkillisen nopeuden (±) suunnaksi ja nopeudeksi.
    Moottorin puoli huomioitu
    """
    if motor_id in STARBOAD_MOTORS:
        return (0, speed) if speed >= 0 else (1, abs(speed))
    else:
        return (1, speed) if speed >= 0 else (0, abs(speed))

def emergency_stop():
    """
    Pysäyttää moottorit välittömästi ja nollaa viimeisen käskyn.
    """
    global _last_command
    try:
        if MODBUS_AVAILABLE:
            modbus_worker.emergency_stop()

        _last_command = None
        logger.warning("Emergency stop executed")
    except Exception:
        logger.exception("Failed to execute emergency stop")

def stop_all_motors():
    """
    Pysäyttää kaikki moottorit.
    """
    try:
        if MODBUS_AVAILABLE:
            modbus_worker.stop_all()
        logger.info("All motors stopped")
    except Exception:
        logger.exception("Failed to stop all motors")