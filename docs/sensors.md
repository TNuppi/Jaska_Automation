## sensors.py

vastaa sensoreiden lukemisesta eri lähteistä, kerätä ne yhteen ja palauttaa SensorData objektina.

```mermaid
flowchart TD

sensors["sensors.py"]
roboconfig["robot_config.py"]
modbusworker["modbus_worker.py"]
types["robot_type.py"]
request["request"]
data["return: <br/> SensorData"]

roboconfig -->|settings| sensors
types -->|"SensorData"| sensors
modbusworker -->|"motor contoller feedback"| sensors
request -.-> |FastAPI | sensors
sensors --> data

classDef datastyle fill:#4EC9B0,stroke:#333,stroke-width:2px
class data datastyle
```
### Funktiot

#### read_camera_depth()
Jos kamera ei ole käytössä niin kameran syvyys arvot ovat äärettömiä jotta robottia pystytään ajamaan.
Muuten kameraan syvyys dataa yritetään lukea HTTP requestillä, mutta dataa ei onnistuta saamaan palautetaan **None** arvot.

```mermaid
flowchart TD
    A([START])
    B{CAMERA_AVAILABLE?}
    B1[robot_config.py]
    C["log: Camera not available"]
    D["return<br/>('inf', 'inf', 'inf')"]

    E["HTTP GET CAMERA_URL<br/>timeout=0.05"]
    F["parse JSON response"]

    G["return<br/>(left, center, right)"]

    H["log error:<br/>Camera read failed"]
    I["return<br/>(None, None, None)"]

    A --> B

    B1 -->|True/False| B
    B1 -->|CAMERA_URL| E
    B -- Ei --> C --> D
    B -- Kyllä --> E

    E --> F --> G
    E -. Exception .-> H --> I


```
#### read_IMU()

Jos IMU ei ole käytössä tai IMUn dataa ei saada requestillä niin arvot ovat **None**

```mermaid
flowchart TD
    A([START])
    B{IMU_AVAILABLE?}
    B1[robot_config.py]
    C["log: IMU not available"]
    D["return<br/>(None, None, None)"]

    E["HTTP GET IMU_URL<br/>timeout=0.05"]
    F["parse JSON response"]

    G["return<br/>(roll_deg, pitch_deg, yaw_deg)"]

    H["log error:<br/>IMU read failed"]
    I["return<br/>(None, None, None)"]

    A --> B

    B1 -->|True/False| B
    B1 -->|IMU_URL| E
    B -- Ei --> C --> D
    B -- Kyllä --> E

    E --> F --> G
    E -. Exception .-> H --> I


```
#### safe_motor_freq()
Luetaan moottorin hall anturin taajuus moottori kortilta modbusworkerin kautta,
jos ei ole mahdollista saada dataa niin palautetaan arvo **None**
```mermaid
flowchart TD
    A([START])
    B{MODBUS_AVAILABLE?}
    B1[robot_config.py]
    C["return None"]

    D["get_status(motor_id)"]
    E["log:<br/>Motor frequency"]

    F{data olemassa?}
    G["return data['frequency_Hz']"]
    H["return None"]

    A --> B
    B1 -->|True/False| B
    B -- Ei --> C
    B -- Kyllä --> D --> E --> F
    F -- Kyllä --> G
    F -- Ei --> H


```

#### safe_motor_voltage()
Luetaan moottori kortille tulevä jännite,
jos ei ole mahdollista saada dataa niin palautetaan arvo **None**
```mermaid
flowchart TD
    A([START])
    B{MODBUS_AVAILABLE?}
    B1[robot_config.py]
    C["return None"]

    D["get_status(motor_id)"]
    E["log:<br/>Motor voltage"]

    F{data olemassa?}
    G["return data['voltage_V']"]
    H["return None"]

    A --> B
    B1 -->|True/False| B
    B -- Ei --> C
    B -- Kyllä --> D --> E --> F
    F -- Kyllä --> G
    F -- Ei --> H


```

#### read_IO_data():
Lisätty mahdollisuus IO:n lukemiseen.
IO1 on varattu hätäseisille ja IO2 on reset napille.
```mermaid
flowchart TD
    %% ===== Lähdeblokki =====
    RC["robot_config.py"]

    %% ===== Funktio =====
    A([START])
    B{IO_AVAILABLE?}

    C["log: IO not available"]
    D["return<br/>(1, 0, 0, 0, 0)"]

    E["HTTP GET IO_URL<br/>timeout=0.05"]
    F["parse JSON response"]

    G["return<br/>(IO1, IO2, IO3, IO4, IO5)"]

    H["log error:<br/>IO read failed"]
    I["return<br/>(0, 0, 0, 0, 0)"]

    %% ===== Virtaus =====
    A --> B
    RC -->|True/False| B
    RC -->|IO_URL| E
    

    B -- Ei --> C --> D
    B -- Kyllä --> E

    E --> F --> G
    E -. Exception .-> H --> I
```

#### read_sensors()
Tällä funktiolla varsinaisesti kerätään kaikki data yhteen SensorData objektiin josta voi muutmoduulit sensori tiedot. 
```mermaid
flowchart TD
    A(["read_sensors()"])

    %% ===== Alikutsut: moottorit =====
    M1["safe_motor_freq(1)"]
    M3["safe_motor_freq(3)"]
    M4["safe_motor_freq(4)"]
    M6["safe_motor_freq(6)"]

    %% ===== Alikutsut: akut =====
    B1["safe_motor_voltage(1)"]
    B2["safe_motor_voltage(4)"]

    %% ===== Alikutsut: kamera =====
    CAM["read_camera_depth()<br/>(left, center, right)"]

    %% ===== Alikutsut: IMU =====
    IMU["read_IMU()<br/>(x, y, z)"]

    %% ===== Alikutsut: IO =====
    IO["read_IO_data()<br/>(IO1..IO5)"]

    %% ===== Palautus =====
    R["SensorData<br/>objekti"]

    %% ===== Virtaus =====
    A --> M1
    A --> M3
    A --> M4
    A --> M6

    A --> B1
    A --> B2

    A --> CAM
    A --> IMU
    A --> IO

    M1 --> R
    M3 --> R
    M4 --> R
    M6 --> R

    B1 --> R
    B2 --> R

    CAM --> R
    IMU --> R
    IO --> R

```