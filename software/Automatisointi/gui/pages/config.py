"""
gui/pages/config.py

Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.

Tämän moduulin tehtävä:
- Tarjota käyttöliittymä robotin konfigurointiin
"""

from nicegui import ui
import json
from robot_config import (
    MAX_LINEAR_SPEED,
    MAX_ANGULAR_SPEED,
    CONFIG_FILE,
    reload_config,
    ChangeableConfig
)

def page():
    ui.label("⚙️ Configuration").classes('text-2xl font-bold mb-4')

    ui.markdown("### Motion limits")

    linear = ui.number(
        label="Default linear speed (m/s)",
        value=ChangeableConfig.DEFAULT_LINEAR_SPEED,
        min=0,
        max=MAX_LINEAR_SPEED,
        step=0.1
    )

    angular = ui.number(
        label="Max angular speed (rad/s)",
        value=ChangeableConfig.DEFAULT_ANGULAR_SPEED,
        min=0,
        max=MAX_ANGULAR_SPEED,
        step=0.1
    )

    backward = ui.number(
        label="Default backward speed (m/s)",
        value=ChangeableConfig.DEFAULT_LINEAR_SPEED_BACKWARD,
        min=-MAX_LINEAR_SPEED,
        max=0,
        step=0.1
    )

    def save():
        # Tallennetaan arvot config-tiedostoon JSON-muodossa
        try:
            config_data = {
                "DEFAULT_LINEAR_SPEED": float(linear.value),
                "DEFAULT_ANGULAR_SPEED": float(angular.value),
                "DEFAULT_LINEAR_SPEED_BACKWARD": float(backward.value)
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
            
            reload_config()    
            ui.notify("Config saved & reloaded ✅", color='green')
        except Exception as e:
            ui.notify(f"Error saving config: {e}", color='red')

    ui.button("💾 Save", on_click=save)
