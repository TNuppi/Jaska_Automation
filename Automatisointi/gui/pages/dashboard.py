"""
gui/pages/dashboard.py

Luonut Tero Nikkola yhdessä ChatGPT-5 mini:n kanssa.
Tämän moduulin tehtävä:
- Näyttää robotin tilan dashboard-sivulla
"""
from nicegui import ui
from state import get_state, get_perception
import math
import logging
from robot_config import DEBUG_DASHBOARD

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG_DASHBOARD else logging.INFO)
def page():
    ui.label("📊 Dashboard").classes("text-2xl font-bold mb-4")

    # ===============================
    # YLIN RIVI: Control / Motion / Obstacle
    # ===============================
    with ui.row().classes("w-full gap-4"):
        with ui.card().classes("w-1/4 p-4"):
            ui.label("Control mode")
            control_label = ui.label("---").classes("text-xl font-bold")

        with ui.card().classes("w-1/4 p-4"):
            ui.label("Motion")
            motion_label = ui.label("---").classes("text-xl font-bold")

        with ui.card().classes("w-1/4 p-4"):
            ui.label("Obstacle")
            obstacle_label = ui.label("---")
        

    # ===============================
    # TOINEN RIVI: Speed / Heading / BATTERY
    # ===============================
    with ui.row().classes("w-full gap-4 mt-4"):

        
        with ui.card().classes("w-1/4 p-4"):
            ui.label("Speed (m/s)")
            speed_label = ui.label("---").classes("text-xl font-bold")

        with ui.card().classes("w-1/4 p-4"):
            ui.label("Heading (°)")
            heading_label = ui.label("---").classes("text-xl font-bold")

   # with ui.row().classes("w-full gap-4 mt-4"):
        with ui.card().classes("w-1/4 p-4"):
            ui.label("🔋 Battery").classes("text-lg font-bold mb-3")

            with ui.column().classes("gap-2"):
                with ui.card().classes("w-full p-2 bg-gray-50"):
                    battery1_label = ui.label("Battery 1: ---").classes("text-sm font-bold font-mono")

                with ui.card().classes("w-full p-2 bg-gray-50"):
                    battery2_label = ui.label("Battery 2: ---").classes("text-sm font-bold font-mono")
    # ===============================
    # KOLMAS RIVI: distance jne.
    # ===============================
    with ui.row().classes("w-full gap-4 mt-4"):
        
        with ui.card().classes("w-1/4 p-4"):
            ui.label("Travelled Distance (m)")
            travellde_label = ui.label("0.0").classes("text-xl font-bold")

    

    # ===============================
    # Päivitysfunktio
    # ===============================
    def refresh():
        state = get_state()
        perception = get_perception()
        logger.debug(f"Dashboard refresh: state={state}, perception={perception}")
        # --- State ---
        control_label.set_text(state.control_type)
        motion_label.set_text(state.motion)
        travellde_label.set_text(f"{state.distance_travelled:.2f}")

        # --- Sensorit / perception ---
        if perception:
            heading = getattr(perception, "heading", None)
            velocity = getattr(perception, "measured_velocity", None)
            obstacle_front = getattr(perception, "obstacle_front", "---")
            obstacle_near = getattr(perception, "obstacle_near", "---")
            battery1 = getattr(perception, "battery1", None)
            battery2 = getattr(perception, "battery2", None)

            heading_label.set_text(f"{math.degrees(heading):.1f}°" if heading is not None else "---")
            speed_label.set_text(f"{velocity:.2f}" if velocity is not None else "---")
            obstacle_label.set_text(f"Front: {obstacle_front} / Near: {obstacle_near}")
            battery1_label.set_text(f"Battery 1: {battery1:.2f} V" if battery1 is not None else "Battery 1: ---")
            battery2_label.set_text(f"Battery 2: {battery2:.2f} V" if battery2 is not None else "Battery 2: ---")
        else:
            heading_label.set_text("---")
            speed_label.set_text("---")
            obstacle_label.set_text("Front: --- / Near: ---")
            battery1_label.set_text("Battery 1: ---")
            battery2_label.set_text("Battery 2: ---")

    ui.timer(0.2, refresh)
