"""
gui/app.py
Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.
Tämän moduulin tehtävä:
- Käynnistää ja hallinnoi robotin GUI:ta NiceGUI:llä
- sivujen navigointi
- hätäseis ja muut pysyvät napit

HUOM:
- Ei robottispesifistä logiikkaa
"""

from nicegui import ui, app
import logging
from control import apply_control
from state import request_stop, update_state
from robot_config import DEBUG_APP

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG_APP else logging.INFO)

def start_gui():

# ----------------- GUI Navigointi -----------------
    def navigation():
        with ui.column().classes('w-64 bg-gray-200 p-4'):
            ui.label('🤖 Robot GUI').classes('text-xl font-bold')
            ui.link('Dashboard', '/')
            ui.link('Control', '/control')
            # ui.link('State', '/state')
            ui.separator()
            ui.link('Config', '/config')
            ui.link('Errors', '/errors')
# ----------------- PYSYVÄT NAPIT -----------------
            with ui.button_group():
                ui.button('EMERGENCY STOP', color='red', on_click=emergency_stop)
                ui.button('RESET ROBOT', color='blue', on_click=reseet_dialog)
            ui.button('STOP PROGRAM', color='orange', on_click=stop_dialog)
            
  # ----------------- HÄTÄSEIS napin käsittely -----------------          
    def emergency_stop():
        update_state(status="ERROR", motion="STOP")
        ui.notify("HÄTÄSTOP AKTIIVINEN")
        logger.warning("Emergency stop pressed")

# ----------------- STOP dialogi -----------------
    def stop_dialog():
        with ui.dialog() as dialog, ui.card():
            ui.label("Pysäytetäänkö ohjelma?")
            with ui.row():
                ui.button("Kyllä", color='blue',
                          on_click=lambda: stop_program(dialog))
                ui.button("Ei", color='red', on_click=dialog.close)
        dialog.open()
# ----------------- RESET dialogi -----------------
    def reseet_dialog():
        with ui.dialog() as dialog, ui.card():
            ui.label("Resetoidaanko robotti?")
            with ui.row():
                ui.button("Kyllä", color='blue',
                          on_click=lambda: ResetRobot(dialog))
                ui.button("Ei", color='red', on_click=dialog.close)
        dialog.open()
# ----------------- STOP ohjelma funktio -----------------
    def stop_program(dialog):
        request_stop()
        logger.info("Program stop requested")
        dialog.close()
        ui.notify("Ohjelma pysäytetään")
        
        app.shutdown()
 # ----------------- RESET ROBOTTI funktio -----------------   
    def ResetRobot(dialog):
        update_state(status="OK")
        logger.info("Robot reset requested")
        dialog.close()
        ui.notify("Robotti resetoitu")
        

    # 🔥 TÄRKEÄ: kaikki UI VAIN sivufunktioissa
    @ui.page('/')
    def dashboard_page():
        navigation()
        from .pages.dashboard import page
        page()

    @ui.page('/control')
    def control_page():
        navigation()
        from .pages.control import page
        page()

    # @ui.page('/state')
    # def state_page():
    #     navigation()
    #     from .pages.state import page
    #     page()

    @ui.page('/config')
    def config_page():
        navigation()
        from .pages.config import page
        page()

    @ui.page('/errors')
    def errors_page():
        navigation()
        from .pages.errors import page
        page()

    logger.info("Starting GUI on http://localhost:8080")
    ui.run(title="Robot GUI", port=8080 ,reload=False)
    logger.info("GUI stopped")