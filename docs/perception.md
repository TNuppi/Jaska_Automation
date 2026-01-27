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
---
### calculate_motor_rpms(SensorData)
funktio laskeen kaikkien Sensoridatasta olevien moottorien kierrosnopeuden moottori ohjaimen antamasta taajuudesta
jos taajuus on **None** niin annetaan kierrosnopeus 0.0
kierrosnopeus lasketaan freg* RPM_FACTOR. RPM_FACTOR määritellään robot_config.py:ssä. 
funktio palauttaa dictionaryn jossa avaimet on motor1,motor3 motor4 ja motor6.

---

### calculate_heading(SensorData)
Funktio tällä hetkellä välittää vain raakadatan eteenpäin, mutta jatkossa tässä voi tehdä tälle käsittelyitä.

---

### detect_obstacles(SensorData)

Katsotaan onko syvyys mittauksissa todettu että este olisi lähellä tai suoraan edessä joko näkökentän keskellä, vasemmassa reunassa tai oikeassa reunassa.
Rajat OBSTACLE_MIN_DISTANCE ja OBSTACLE_NEAR_DISTANCE määritellään robot_config.py:ssä.



```mermaid

flowchart TD
    A(["detect_obstacles(sensor_data)"])

    B["Muodosta depths:<br/>left / center / right"]
    C["obstacle_front = False<br/>obstacle_near = False"]

    D{"Käy läpi<br/>depths.items()"}

    E["lue depth d<br/>log debug"]

    F{d is None?}
    G["log error:<br/>DATA MISSING"]
    H["obstacle_front = True<br/>obstacle_near = True"]

    I{d == 'nan'?}
    J["log error:<br/>TOO CLOSE"]
    K["obstacle_front = True<br/>obstacle_near = True"]

    L{d == 'inf'?}

    M{d < OBSTACLE_MIN_DISTANCE?}
    N["obstacle_front = True"]

    O{d < OBSTACLE_NEAR_DISTANCE?}
    P["obstacle_near = True"]


    R["return<br/>(obstacle_front,<br/>obstacle_near)"]

    S["robo_config.py"]

    %% ===== Virtaus =====
    A --> B --> C --> D
    D --> E --> F

    F -- Kyllä --> G --> H --> D
    F -- Ei --> I

    I -- Kyllä --> J --> K --> D
    I -- Ei --> L

    L -- Kyllä --> D
    L -- Ei --> M

    M -- Kyllä --> N --> O
    M -- Ei --> O

    O -- Kyllä --> P --> D
    O -- Ei --> D

    D -- Valmis --> R

    S --> M
    S --> O

```

---

### read_IO_states(SensorData)

Lukee sensordatasta IO datan, ja palauttaa dictionaryn.
tällä hetkellä on vain määritelty että IO_data_1 on emmergency_stop ja IO_data_2 on reset_button.

emmergency_stop on määritelty niin että se on False jos IO_data_1 on 1, muuten True.

reset_button on True IO_data_2 on 1 muuten False

muut ei ole vielä käytössä.

----

