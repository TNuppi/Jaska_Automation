from nicegui import ui
import logging
from collections import deque

ERROR_LOG = deque(maxlen=200)  # EI kasva loputtomiin
DISPLAYED_LOGS = set()  # Pitää kirjaa näytetyistä viesteistä

class GuiLogHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.WARNING:
            ERROR_LOG.append(self.format(record))

root_logger = logging.getLogger()

# Lisää handler vain kerran
if not any(isinstance(h, GuiLogHandler) for h in root_logger.handlers):
    handler = GuiLogHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    ))
    root_logger.addHandler(handler)


def page():
    ui.label("🚨 Errors & Warnings").classes('text-2xl font-bold mb-4')

    log_column = ui.column().classes('w-full gap-1')

    def refresh():
        
        
        with log_column:
            for msg in ERROR_LOG:
                if msg in DISPLAYED_LOGS:
                    continue  # skipataan jo näytetyt
                color = 'text-red-600' if '[ERROR]' in msg else 'text-yellow-600'
                ui.label(msg).classes(f'font-mono text-sm {color}')
                DISPLAYED_LOGS.add(msg)

    def clear_logs():
        ERROR_LOG.clear()
        DISPLAYED_LOGS.clear()
        log_column.clear()

    with ui.row().classes('gap-4 mb-4'):
        ui.button("🧹 Clear logs", on_click=clear_logs)
        ui.label("Auto refresh every 1s").classes('text-sm text-gray-500')

    ui.timer(1.0, refresh)
    refresh()
