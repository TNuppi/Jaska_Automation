"""
gui/pages/config.py

Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.

Tämän moduulin tehtävä:
- Tarjota käyttöliittymä robotin konfigurointiin
"""

from nicegui import ui
from robot_config import (
    DEFAULT_LINEAR_SPEED,
    MAX_LINEAR_SPEED,
    MAX_ANGULAR_SPEED,
)

def page():
    ui.label("⚙️ Configuration").classes('text-2xl font-bold mb-4')

    ui.markdown("### Motion limits")

    linear = ui.number(
        label="Default linear speed (m/s)",
        value=DEFAULT_LINEAR_SPEED,
        min=0,
        max=MAX_LINEAR_SPEED,
        step=0.1
    )

    angular = ui.number(
        label="Max angular speed (rad/s)",
        value=MAX_ANGULAR_SPEED,
        min=0,
        max=6.28,
        step=0.1
    )

    def save():
        ui.notify("Config saved (not yet persistent)", color='green')

    ui.button("💾 Save", on_click=save)
