import logging
from robot_types import PerceptionData, ControlCommand
from robot_config import DEFAULT_LINEAR_SPEED, DEFAULT_ANGULAR_SPEED
from state import get_state, update_state,get_distance_info, add_distance_travelled
logger = logging.getLogger(__name__)

# ----------------- HELPER FUNKTIOT -----------------
def stop() -> ControlCommand:
    return ControlCommand(linear_speed=0.0, angular_speed=0.0)

def drive_forward() -> ControlCommand:
    return ControlCommand(linear_speed=DEFAULT_LINEAR_SPEED, angular_speed=0.0)

def drive_slow_forward() -> ControlCommand:
    return ControlCommand(linear_speed=DEFAULT_LINEAR_SPEED * 0.5, angular_speed=0.0)

def drive_backward() -> ControlCommand:
    return ControlCommand(linear_speed=-DEFAULT_LINEAR_SPEED * 0.3, angular_speed=0.0)

def turn_left() -> ControlCommand:
    return ControlCommand(linear_speed=0.0, angular_speed=DEFAULT_ANGULAR_SPEED)

def turn_right() -> ControlCommand:
    return ControlCommand(linear_speed=0.0, angular_speed=-DEFAULT_ANGULAR_SPEED)

def turn() -> ControlCommand:
    return ControlCommand(linear_speed=DEFAULT_LINEAR_SPEED * 0.5, angular_speed=DEFAULT_ANGULAR_SPEED)

# ----------------- PÄÄFUNKTIO -----------------
def decide(perception: PerceptionData) -> ControlCommand:
    """
    Päätöksenteko robottiohjaukseen.
    Käyttää suoraan singleton robot_state.
    """
    state = get_state()
    
    # --- MANUAL TILA ---
    if state.control_type == "MAN":
        if state.motion == "MAN_FORWARD":
            return handle_manual_forward(perception)
        if state.motion == "MAN_BACKWARD":
            return handle_manual_backward(perception)
        if state.motion == "MAN_LEFT":
            return handle_manual_turn_left(perception)
        if state.motion == "MAN_RIGHT":
            return handle_manual_turn_right(perception)
        if state.motion == "STOP":
            return stop()
    elif state.control_type == "ERROR":
        return handle_error()

    # --- AUTO TILA ---
    else:
        if state.motion == "STOP":
            return stop()
        if state.motion == "FORWARD":
            return handle_forward(perception)
        if state.motion == "SLOW_FORWARD":
            return handle_slow_forward(perception)
        if state.motion == "AVOIDING":
            return turn()
        if state.motion == "DRIVE_DISTANCE":
            return handle_drive_distance(perception)
        if state.motion == "WAIT":
            return handle_wait(perception)

    # Tuntematon tila -> pysäytä
    logger.error(f"Unknown state: {state.motion}, stopping")
    update_state(control_type="ERROR")
    return stop()

# ----------------- ERROR HANDLER -----------------
def handle_error() -> ControlCommand:
    logger.error("In ERROR state, stopping robot")
    return stop()

# ----------------- MANUAL HANDLERS -----------------
def handle_manual_forward(perception):
    if perception.obstacle_near:
        return stop()
    if perception.obstacle_front:
        return drive_slow_forward()
    return drive_forward()

def handle_manual_backward(perception):
    return drive_backward()

def handle_manual_turn_left(perception):
    return turn_left()

def handle_manual_turn_right(perception):
    return turn_right()

# ----------------- AUTO HANDLERS -----------------
def handle_forward(perception):
    if perception.obstacle_near:
        update_state(motion="WAIT")
        return stop()
    if perception.obstacle_front:
        update_state(motion="SLOW_FORWARD")
        return drive_slow_forward()
    return drive_forward()

def handle_slow_forward(perception):
    if perception.obstacle_near:
        update_state(motion="WAIT")
        return stop()
    if not perception.obstacle_front:
        update_state(motion="FORWARD")
        return drive_forward()
    return drive_slow_forward()

def handle_drive_distance(perception):
    start, target, travelled = get_distance_info()
    
    if target is None:
        logger.error("Drive distance target is None, stopping")
        update_state(motion="STOP")
        return stop()
    
    if travelled >= target:
        logger.info(f"Reached target distance: {travelled:.2f} m >= {target:.2f} m")
        update_state(
            motion="STOP",
            start_distance=None, 
            target_distance=None
            )
        return stop()
    
    if perception.obstacle_near:
        update_state(motion="WAIT")
        return stop()
    
    if perception.obstacle_front:
        return drive_slow_forward()
    
    return drive_forward()

def handle_wait(perception):
    if perception.obstacle_near:
        return stop()
    state = get_state()
    previous_motion = state.last_motion or "FORWARD"
    update_state(motion=previous_motion)
    if previous_motion == "FORWARD": return drive_forward()
    if previous_motion == "SLOW_FORWARD": return drive_slow_forward()
    if previous_motion == "AVOIDING": return turn()
    return drive_forward()

# ----------------- GUI HELPERS -----------------
def gui_set_manual():
    logger.info("GUI requested MANUAL mode")
    update_state(control_type="MAN", motion="STOP")
def gui_set_auto():
    logger.info("GUI requested AUTO mode")
    update_state(control_type="AUTO", motion="STOP")
def gui_request_stop():
    logger.info("GUI requested STOP")
    update_state(motion="STOP")
def gui_man_forward():
    logger.info("GUI requested MAN_FORWARD")
    update_state(motion="MAN_FORWARD")
def gui_man_backward():
    logger.info("GUI requested MAN_BACKWARD")
    update_state(motion="MAN_BACKWARD") 
def gui_man_left():
    logger.info("GUI requested  MAN_LEFT")
    update_state(motion="MAN_LEFT")
def gui_man_right():
    logger.info("GUI requested MAN_RIGHT")
    update_state(motion="MAN_RIGHT")