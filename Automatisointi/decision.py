import logging
from robot_types import PerceptionData, ControlCommand
from robot_config import DEFAULT_LINEAR_SPEED, DEFAULT_ANGULAR_SPEED
from state import robot_state
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

# ----------------- PÄÄFUNKTI -----------------
def decide(perception: PerceptionData) -> ControlCommand:
    """
    Päätöksenteko robottiohjaukseen.
    Käyttää suoraan singleton robot_state.
    """
    state = robot_state.get_state()
    
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
    robot_state.update_state(motion="STOP")
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
        robot_state.update_state(motion="WAIT")
        return stop()
    if perception.obstacle_front:
        robot_state.update_state(motion="SLOW_FORWARD")
        return drive_slow_forward()
    return drive_forward()

def handle_slow_forward(perception):
    if perception.obstacle_near:
        robot_state.update_state(motion="WAIT")
        return stop()
    if not perception.obstacle_front:
        robot_state.update_state(motion="FORWARD")
        return drive_forward()
    return drive_slow_forward()

def handle_drive_distance(perception):
    start, target = robot_state.get_distance_info()
    state = robot_state.get_state()
    if start is None or target is None:
        robot_state.update_state(motion="STOP")
        return stop()
    travelled = state.distance_travelled - start
    if travelled >= target:
        robot_state.update_state(motion="STOP", start_distance=None, target_distance=None)
        return stop()
    if perception.obstacle_near:
        robot_state.update_state(motion="WAIT")
        return stop()
    robot_state.add_distance_travelled(perception.measured_velocity * 0.1)
    return drive_forward()

def handle_wait(perception):
    if perception.obstacle_near:
        return stop()
    state = robot_state.get_state()
    previous_motion = state.last_motion or "FORWARD"
    robot_state.update_state(motion=previous_motion)
    if previous_motion == "FORWARD": return drive_forward()
    if previous_motion == "SLOW_FORWARD": return drive_slow_forward()
    if previous_motion == "AVOIDING": return turn()
    return drive_forward()
