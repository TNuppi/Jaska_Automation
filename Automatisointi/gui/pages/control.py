# gui/pages/control.py
from nicegui import ui
from state import update_state, get_state

import logging
import decision

logger = logging.getLogger(__name__)

def page():
    ui.label('🕹 Manual Control').classes('text-xl font-bold mb-4')

    # --- Funktiot ---
    def toggle_manual():
        """Kytkee MAN/AUTO-tilan päälle tai pois"""
        state = get_state()
        if state.control_type == "AUTO":
            decision.gui_set_manual()
            logger.info(f"Manual mode activated. RobotState id={id(get_state())}")
        else:
            decision.gui_set_auto()
            logger.info(f"Manual mode deactivated. RobotState id={id(get_state())}")

    def toggle_motion(motion: str):
        """Kytkee päälle painetun motionin tai STOP jos sama painetaan uudelleen"""
        state = get_state()
        if state.control_type != "MAN":
            return  # Ei tee mitään jos ei MAN-tila
        if state.motion != motion:
            update_state(motion=motion)
            logger.info(f"Manual motion: {motion}")
        else:
            update_state(motion="STOP")
            logger.info("Manual motion: STOP")

    # --- Toggle MAN/AUTO ---
    ui.button("Toggle MAN/AUTO", on_click=lambda _: toggle_manual()).classes('mb-4')

    # --- Liike napit ---
    with ui.column().classes('items-center gap-4'):
        ui.button('⬆ Forward', on_click=decision.gui_man_forward)
        ui.button('⬇ Backward', on_click=decision.gui_man_backward)
        with ui.row().classes('gap-4'):
            ui.button('⬅ Left', on_click=decision.gui_man_left)
            ui.button('➡ Right', on_click=decision.gui_man_right)
            ui.button('⏹ Stop', on_click=decision.gui_request_stop)
    # --- Nykyinen tila label ---
    state_label = ui.label()

    def refresh_label():
        """Päivittää GUI:n labelin robotin nykyisen tilan mukaan"""
        state = get_state()
        state_label.text = f"Control: {state.control_type}, Motion: {state.motion}"

    # Päivitetään label 5 kertaa sekunnissa
    ui.timer(0.2, refresh_label)
