# gui/app.py
from nicegui import ui, app
import logging
from control import apply_control
from state import request_stop

logger = logging.getLogger(__name__)

def start_gui():

    def navigation():
        with ui.column().classes('w-64 bg-gray-200 p-4'):
            ui.label('🤖 Robot GUI').classes('text-xl font-bold')
            ui.link('Dashboard', '/')
            ui.link('Control', '/control')
            # ui.link('State', '/state')
            ui.separator()
            ui.link('Config', '/config')
            ui.link('Errors', '/errors')

            ui.button('EMERGENCY STOP', color='red', on_click=emergency_stop)
            ui.button('STOP PROGRAM', color='orange', on_click=stop_dialog)

    def emergency_stop():
        apply_control(None)
        ui.notify("HÄTÄSTOP AKTIIVINEN")
        logger.warning("Emergency stop pressed")

    def stop_dialog():
        with ui.dialog() as dialog, ui.card():
            ui.label("Pysäytetäänkö ohjelma?")
            with ui.row():
                ui.button("Kyllä", color='red',
                          on_click=lambda: stop_program(dialog))
                ui.button("Ei", on_click=dialog.close)
        dialog.open()

    def stop_program(dialog):
        apply_control(None)
        request_stop()
        dialog.close()
        ui.notify("Ohjelma pysäytetään")
        logger.info("Program stop requested")
        app.shutdown()

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