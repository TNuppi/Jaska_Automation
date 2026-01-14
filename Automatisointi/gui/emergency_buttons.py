# gui/emergency_buttons.py
from nicegui import ui
import logging
from control import apply_control  # käytetään apply_control(hätästop)
from state import stop_flag

logger = logging.getLogger(__name__)

def add_global_controls():
    ui.button('EMERGENCY STOP', color='red', on_click=lambda: emergency_stop_action())
    ui.button('STOP PROGRAM', color='orange', on_click=lambda: stop_program_dialog())

def emergency_stop_action():
    apply_control(None, emergency_stop=True)
    logger.warning("EMERGENCY STOP pressed from GUI")
    ui.notify("Moottorit pysähtyivät välittömästi!")

def stop_program_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label("Haluatko varmasti pysäyttää ohjelman?")
        with ui.row():
            ui.button("Kyllä", on_click=lambda: stop_program(dialog), color='red')
            ui.button("Ei", on_click=dialog.close)
    dialog.open()

def stop_program(dialog):
    global stop_flag
    apply_control(None, emergency_stop=True)
    stop_flag = True
    ui.notify("Ohjelma pysähtyy...")
    logger.info("STOP PROGRAM pressed from GUI")
    dialog.close()
