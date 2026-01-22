"""
decision.py

Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.
Tämän moduulin tehtävä:
- Päätöksenteko robottiohjaukseen
"""


import logging
from robot_types import PerceptionData, ControlCommand
from robot_config import DEBUG_DECISIONS, ChangeableConfig
from state import get_state, update_state,get_distance_info, add_distance_travelled
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG_DECISIONS else logging.INFO)

# ----------------- HELPER FUNKTIOT -----------------
def stop() -> ControlCommand:
    return ControlCommand(linear_speed=0.0, angular_speed=0.0)

def drive_forward() -> ControlCommand:
    return ControlCommand(linear_speed=ChangeableConfig.DEFAULT_LINEAR_SPEED, angular_speed=0.0)

def drive_slow_forward() -> ControlCommand:
    return ControlCommand(linear_speed=ChangeableConfig.DEFAULT_LINEAR_SPEED * 0.5, angular_speed=0.0)

def drive_backward() -> ControlCommand:
    return ControlCommand(linear_speed=ChangeableConfig.DEFAULT_LINEAR_SPEED_BACKWARD, angular_speed=0.0)

def turn_left() -> ControlCommand:
    return ControlCommand(linear_speed=0.0, angular_speed=ChangeableConfig.DEFAULT_ANGULAR_SPEED)

def turn_right() -> ControlCommand:
    return ControlCommand(linear_speed=0.0, angular_speed=-ChangeableConfig.DEFAULT_ANGULAR_SPEED)

def turn() -> ControlCommand:
    return ControlCommand(linear_speed=ChangeableConfig.DEFAULT_LINEAR_SPEED * 0.5, angular_speed=ChangeableConfig.DEFAULT_ANGULAR_SPEED)

# ----------------- PÄÄFUNKTIO -----------------
def decide(perception: PerceptionData) -> ControlCommand:
    """
    Päätöksenteko robottiohjaukseen.
    Päätökset perustuvat robotin tilaan ja havainnointiin.
    Palauttaa ControlCommand-olion.
    """
    robot_states = get_state()
    emmergency_stop_button_S50 = perception.emmergency_stop
    restebutton = perception.reset_button
    prev_resetbutton = robot_states.prev_reset_button

    # --- HÄTÄSEIS TARKISTUS ---
    if emmergency_stop_button_S50:
        logger.warning("Emergency stop (S50) activated!")
        update_state(status="ERROR", motion="STOP")
        return stop()
    
    # --- RESET NAPIN TARKISTUS ---
    reset_edge = not prev_resetbutton and restebutton

    # --- VIRHETILASTA OK TILAAN PALUU VAIN RESET NAPIN NOUSEVALLA REUNALLA ---
    if robot_states.status == "ERROR" and not emmergency_stop_button_S50:
        if reset_edge:
            logger.info("Emergency stop released, returning to OK status")
            update_state(status="OK")

    
    # --- VIRHETILA ---
    if robot_states.status != "OK":
        update_state(control_type="ERROR")
        update_state(prev_reset_button=restebutton)
        return handle_error()
    
    # --- Virhe tilasta palautuminen ---
    if robot_states.status == "OK":
        if robot_states.last_status != "OK":
            logger.info("Status OK")
            update_state(control_type="MAN", motion="STOP")
        update_state(last_status="OK")
    # --- MANUAL TILA ---
    if robot_states.control_type == "MAN":
        if robot_states.motion == "MAN_FORWARD":
            return handle_manual_forward(perception)
        if robot_states.motion == "MAN_BACKWARD":
            return handle_manual_backward(perception)
        if robot_states.motion == "MAN_LEFT":
            return handle_manual_turn_left(perception)
        if robot_states.motion == "MAN_RIGHT":
            return handle_manual_turn_right(perception)
        if robot_states.motion == "STOP":
            return stop()


    # --- AUTO TILA ---
    else:
        if robot_states.motion == "STOP":
            return stop()
        if robot_states.motion == "FORWARD":
            return handle_forward(perception)
        if robot_states.motion == "SLOW_FORWARD":
            return handle_slow_forward(perception)
        if robot_states.motion == "AVOIDING":
            return turn()
        if robot_states.motion == "DRIVE_DISTANCE":
            return handle_drive_distance(perception)
        if robot_states.motion == "WAIT":
            return handle_wait(perception)

    # Tuntematon tila -> pysäytä
    logger.error(f"Unknown state: {robot_states.motion}, stopping")
    update_state(status="ERROR" ,motion="STOP")
    return stop()

# ----------------- ERROR HANDLER -----------------
def handle_error() -> ControlCommand:
    robot_states = get_state()
    if robot_states.last_status != "ERROR":
        logger.error("In ERROR state, stopping robot")
        update_state(last_status="ERROR")
    return stop()

# ----------------- MANUAL HANDLERS -----------------
def handle_manual_forward(perception):
    if perception.obstacle_near and not perception.obstacle_front:
        return drive_slow_forward()
    if perception.obstacle_front:
        return stop()
    return drive_forward()

def handle_manual_backward(perception):
    return drive_backward()

def handle_manual_turn_left(perception):
    return turn_left()

def handle_manual_turn_right(perception):
    return turn_right()

# ----------------- AUTO HANDLERS -----------------
def handle_forward(perception):
    state = get_state()
    if perception.obstacle_near:
        update_state(motion="SLOW_FORWARD", last_motion= state.motion )
        return stop()
    if perception.obstacle_front:
        update_state(motion="WAIT", last_motion= state.motion)
        return drive_slow_forward()
    return drive_forward()

def handle_slow_forward(perception):
    state = get_state()
    if not perception.obstacle_near:
        update_state(motion=state.last_motion, last_motion= state.motion)
        return drive_slow_forward()
    if perception.obstacle_front:
        update_state(motion="WAIT", last_motion= state.motion)
        return stop()
    return drive_slow_forward()

def handle_drive_distance(perception):
    start, target, travelled = get_distance_info()
    state = get_state()
    if target is None:
        logger.error("Drive distance target is None, stopping")
        update_state(motion="STOP", last_motion= state.motion ,target_distance=0.0)
        return stop()
    
    if travelled >= target:
        logger.info(f"Reached target distance: {travelled:.2f} m >= {target:.2f} m")
        update_state(
            motion="STOP",
            last_motion= state.motion,
            start_distance=travelled
            )
        return stop()
    
    if perception.obstacle_near and not perception.obstacle_front:
        
        return drive_slow_forward()
    
    if perception.obstacle_front:
        update_state(motion="WAIT", last_motion= state.motion)
        return stop()
    
    return drive_forward()

def handle_wait(perception):

    
    if not perception.obstacle_front:
        state = get_state()
        previous_motion = state.last_motion or "STOP"
        update_state(motion=previous_motion)
        if previous_motion == "DRIVE_DISTANCE": return drive_slow_forward()
        if previous_motion == "FORWARD": return drive_forward()
        if previous_motion == "SLOW_FORWARD": return drive_slow_forward()
        if previous_motion == "AVOIDING": return turn()
        if previous_motion == "STOP":return stop()
    return stop()

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