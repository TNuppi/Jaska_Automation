from nicegui import ui
from state import get_state, get_perception
import math

def page():
    ui.label("📊 Dashboard").classes("text-xl font-bold mb-4")

    heading_label = ui.label("Heading: 0.0°")
    velocity_label = ui.label("Velocity: 0.0 m/s")
    motion_label = ui.label("Motion: ---")
    control_type_label = ui.label("Control: ---")
    obstacle_label = ui.label("Obstacle front / near: ---")

    def refresh():
        state = get_state()
        perception = get_perception()

        control_type_label.set_text(f"Control: {state.control_type}")
        motion_label.set_text(f"Motion: {state.motion}")

        if perception:
            heading = perception.heading if perception.heading is not None else 0.0
            velocity = perception.measured_velocity if perception.measured_velocity is not None else 0.0
            obstacle_label.set_text(
                f"Obstacle front: {perception.obstacle_front}, "
                f"Obstacle near: {perception.obstacle_near}"
            )
        else:
            heading = 0.0
            velocity = 0.0
            obstacle_label.set_text("Obstacle front: --- / near: ---")

        heading_label.set_text(f"Heading: {math.degrees(heading):.1f}°")
        velocity_label.set_text(f"Velocity: {velocity:.2f} m/s")

    ui.timer(0.2, refresh)
