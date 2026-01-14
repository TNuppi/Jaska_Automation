# gui/pages/control.py
from nicegui import ui
from state import set_manual_mode, set_auto_mode, robot_state
from control import testi_man, testi_auto
import logging

logger = logging.getLogger(__name__)

def page():
    ui.label('🕹 Manual Control').classes('text-xl font-bold mb-4')

    # --- Funktiot ---
    def toggle_manual():
        """Kytkee MAN/AUTO-tilan päälle tai pois"""
        state = robot_state.get_state()
        if state.control_type == "AUTO":
            testi_auto()
            logger.info(f"Manual mode activated. RobotState id={id(robot_state.get_state())}")
        else:
            testi_man()
            logger.info(f"Manual mode deactivated. RobotState id={id(robot_state.get_state())}")

    def toggle_motion(motion: str):
        """Kytkee päälle painetun motionin tai STOP jos sama painetaan uudelleen"""
        state = robot_state.get_state()
        if state.control_type != "MAN":
            return  # Ei tee mitään jos ei MAN-tila
        if state.motion != motion:
            robot_state.update_state(motion=motion)
            logger.info(f"Manual motion: {motion}")
        else:
            robot_state.update_state(motion="STOP")
            logger.info("Manual motion: STOP")

    # --- Toggle MAN/AUTO ---
    ui.button("Toggle MAN/AUTO", on_click=lambda _: toggle_manual()).classes('mb-4')

    # --- Liike napit ---
    with ui.column().classes('items-center gap-4'):
        ui.button('⬆ Forward', on_click=lambda _: toggle_motion("MAN_FORWARD"))
        ui.button('⬇ Backward', on_click=lambda _: toggle_motion("MAN_BACKWARD"))
        with ui.row().classes('gap-4'):
            ui.button('⬅ Left', on_click=lambda _: toggle_motion("MAN_LEFT"))
            ui.button('➡ Right', on_click=lambda _: toggle_motion("MAN_RIGHT"))

    # --- Nykyinen tila label ---
    state_label = ui.label()

    def refresh_label():
        """Päivittää GUI:n labelin robotin nykyisen tilan mukaan"""
        state = robot_state.get_state()
        state_label.text = f"Control: {state.control_type}, Motion: {state.motion}"

    # Päivitetään label 5 kertaa sekunnissa
    ui.timer(0.2, refresh_label)
