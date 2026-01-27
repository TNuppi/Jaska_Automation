# Perception.py


Moduulin tehtävänä on lukea SensorData ja käsitellä haluttuun muotoon. 
Moduulin käsittelemät SensorData kerätään yhteen ja palautetaan PerceptionData objektina.

```mermaid
flowchart TD

types["robot_type.py"]
config["robot_config.py"]
perception["perception.py"]
data["return: </br> PerceptionData "]

types -->|SensorData| perception
types -->|PerceptionData| perception
config -->|settings| perception
perception --> data

classDef datastyle fill:#4EC9B0,stroke:#333,stroke-width:2px
class data datastyle

```

## Funktiot

moduulin pääfunktio jota käytetään mainissa. suorittaa käsittelyt ja kerää käsitellun datan yhteen paikkaan.
### perceive()

```mermaid

flowchart TD
    A(["perceive(sensor_data)"])

    %% ===== Laskennat =====
    B["calculate_motor_rpms(sensor_data)"]
    C["calculate_linear_velocity(rpms)"]
    D["calculate_heading(sensor_data)"]
    E["detect_obstacles(sensor_data)"]

    %% ===== IO & akut =====
    F["read_IO_states(sensor_data)"]
    G["battery1_voltage<br/>battery2_voltage"]

    %% ===== Palautusolio =====
    H["PerceptionData<br/>objekti"]

    %% ===== Virtaus =====
    A --> B
    B --> C
    A --> D
    A --> E
    A --> F
    A --> G

    B --> H
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H

classDef datastyle fill:#4EC9B0,stroke:#333,stroke-width:2px
class H datastyle

```