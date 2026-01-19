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
            logger.info(f"Starting DRIVE_DISTANCE to {target:.2f} m")
            update_state(motion="DRIVE_DISTANCE", start_distance=0.0, target_distance=target)

        ui.button('Start', on_click=start_drive_distance).classes('w-40')
        # --- Progress bar ---
        progress_bar = ui.linear_progress(show_value=False,size="10px")


    # ===============================
    # TILAN NÄYTTÖ
    # ===============================
    state_label = ui.label().classes('mt-6 font-mono')
    velocity_label = ui.label().classes('font-mono')
    distance_label = ui.label().classes('font-mono')

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

        # --- Näytä/piilota paneelit ---
        manual_container.visible = (state.control_type == "MAN")
        drive_distance_container.visible = (state.control_type == "AUTO")

        # Päivitä kytkin jos tila muuttuu muualla
        mode_switch.value = (state.control_type == "MAN")

                # --- Progress bar update ---
        if state.motion == "DRIVE_DISTANCE" and state.target_distance:
            progress = min(state.distance_travelled / state.target_distance, 1.0)
            progress_bar.value = progress
        else:
            progress_bar.value = 0

    ui.timer(0.2, refresh)
