# gui/pages/control.py
from nicegui import ui
from state import update_state, get_state, get_perception
import decision
import logging

logger = logging.getLogger(__name__)


def page():
    ui.label('🕹 Control').classes('text-xl font-bold mb-4')

    # ===============================
    # MAN / AUTO - KYTKIN
    # ===============================
    def on_mode_change(e):
        if e.value:
            decision.gui_set_manual()
            logger.info("MANUAL mode selected from switch")
        else:
            decision.gui_set_auto()
            logger.info("AUTO mode selected from switch")

    mode_switch = ui.switch(
        text='Manual mode',
        value=(get_state().control_type == "MAN"),
        on_change=on_mode_change,
    ).classes('mb-6')

    # ===============================
    # MANUAL CONTROL - KONTTI
    # ===============================
    manual_container = ui.column().classes('items-center gap-4 touch-none')
    with manual_container:
        def man_button(label, start_fn):
            btn = ui.button(label).classes('touch-none select-none w-40')

            def safe_start():
                state = get_state()
                if state.control_type == "MAN":
                    start_fn()
                else:
                    logger.debug("Ignored manual command: not in MAN mode")

            btn.on('pointerdown', lambda _: safe_start())
            btn.on('pointerup', lambda _: decision.gui_request_stop())
            btn.on('pointerleave', lambda _: decision.gui_request_stop())
            btn.on('pointercancel', lambda _: decision.gui_request_stop())
            return btn

        man_button('⬆ Forward', decision.gui_man_forward)

        with ui.row().classes('gap-4'):
            man_button('⬅ Left', decision.gui_man_left)
            man_button('➡ Right', decision.gui_man_right)

        man_button('⬇ Backward', decision.gui_man_backward)
        ui.button('Reset Distance', on_click=lambda: update_state(distance_travelled=0.0)).classes('w-40 mt-4')

    # ===============================
    # DRIVE DISTANCE - KONTTI
    # ===============================
    drive_distance_container = ui.column().classes('items-center gap-4 touch-none')

    with drive_distance_container:
        ui.label('Drive Distance (AUTO)').classes('font-bold')

        target_input = ui.input(
            label='Target Distance (m)',
            placeholder='Enter target distance'
            ).props("type=number").classes('w-40')


        def start_drive_distance():
            try:
                target = float(target_input.value)
            except (ValueError, TypeError):
                logger.warning("Invalid target distance")
                return
            state = get_state()
            logger.info(f"Starting DRIVE_DISTANCE to {target:.2f} m")
            update_state(motion="DRIVE_DISTANCE", target_distance=target, start_distance=state.distance_travelled)

        def stop_drive_distance():
            state = get_state()
            logger.info("Stopping DRIVE_DISTANCE")
            update_state(motion="STOP", start_distance=state.distance_travelled, target_distance=state.target_distance)
        
        def reset_distance_travelled():
            logger.info("Resetting distance travelled to 0.0 m")
            update_state(distance_travelled=0.0, start_distance=0.0, target_distance=0.0)
        with ui.button_group():
            ui.button('Start', color='green', on_click=start_drive_distance).classes('w-40')
            ui.button('Stop', color='red', on_click=stop_drive_distance).classes('w-40')
            ui.button('Reset Distance', on_click=reset_distance_travelled).classes('w-40')
        # --- Progress bar ---
        progress_bar = ui.linear_progress(show_value=False,size="20px")
        distance_label = ui.label().classes('font-mono')
        start_distance_label = ui.label().classes('font-mono')
        target_distance_label = ui.label().classes('font-mono')

    # ===============================
    # TILAN NÄYTTÖ
    # ===============================
    state_label = ui.label().classes('mt-6 font-mono')
    velocity_label = ui.label().classes('font-mono')
    

    # ===============================
    # TIMERI / PÄIVITYS
    # ===============================
    def refresh():
        state = get_state()
        perception = get_perception()

        # --- Tila ja sensorit ---
        state_label.text = f"Control: {state.control_type} | Motion: {state.motion}"
        velocity_label.text = (
            f"Velocity: {perception.measured_velocity:.2f} m/s"
            if perception and perception.measured_velocity is not None
            else "Velocity: --- m/s"
        )
        distance_label.text = f"Distance travelled: {state.distance_travelled:.2f} m"
        start_distance_label.text = f"Start distance: {state.start_distance:.2f} m"
        target_distance_label.text = (f"Target distance: {state.target_distance:.2f} m"
            if state.target_distance is not None else "Target distance: --- m")

        # --- Näytä/piilota paneelit ---
        manual_container.visible = (state.control_type == "MAN")
        drive_distance_container.visible = (state.control_type == "AUTO")

        # Päivitä kytkin jos tila muuttuu muualla
        mode_switch.value = (state.control_type == "MAN")

             # --- Progress bar update --   
         # distance kuljettu suhteessa start_distanceen
        distance_done = state.distance_travelled
        progress_total = state.target_distance  
         # Suojaa nollalla, ettei jaeta nollalla
        if progress_total is None or progress_total <= 0:
            progress = 0
        else:
            progress = max(0.0, min(distance_done / progress_total, 1.0))   
        progress_bar.value = progress
        
    

    ui.timer(0.2, refresh)
