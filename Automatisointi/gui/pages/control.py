# gui/pages/control.py
from nicegui import ui
from state import update_state, get_state
import decision
import logging

logger = logging.getLogger(__name__)


def page():
    ui.label('🕹 Manual Control').classes('text-xl font-bold mb-4')

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
    # MANUAALILIKE – PAINA = LIIKE, IRTI = STOP
    # ===============================
    def man_button(label, start_fn):
        btn = ui.button(label).classes(
            'touch-none select-none w-40'
        )

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


    with ui.column().classes('items-center gap-4 touch-none'):
        man_button('⬆ Forward', decision.gui_man_forward)

        with ui.row().classes('gap-4'):
            man_button('⬅ Left', decision.gui_man_left)
            man_button('➡ Right', decision.gui_man_right)

        man_button('⬇ Backward', decision.gui_man_backward)
       


    # ===============================
    # TILAN NÄYTTÖ
    # ===============================
    state_label = ui.label().classes('mt-6 font-mono')

    def refresh_label():
        state = get_state()
        state_label.text = f"Control: {state.control_type} | Motion: {state.motion}"

        # Päivitä kytkin jos tila muuttuu muualla
        mode_switch.value = (state.control_type == "MAN")

    ui.timer(0.2, refresh_label)
