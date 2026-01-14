from nicegui import ui
import logging

# yksinkertainen logipuskuri
ERROR_LOG = []

class GuiLogHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.WARNING:
            ERROR_LOG.append(self.format(record))

handler = GuiLogHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(handler)


def page():
    ui.label("🚨 Errors & Warnings").classes('text-2xl font-bold mb-4')

    log_column = ui.column().classes('w-full')

    def refresh():
        log_column.clear()
        for msg in ERROR_LOG[-50:]:
            ui.label(msg).classes('text-red-600')

    ui.button("🔄 Refresh", on_click=refresh)
    refresh()
