## main.py

main ei sisällä mitään robotti spesifistä logiikkaa

mainin tehtänä on käynnistää:
1. control looppi omassa säikeessä
2. käynnistää gui
3. käynnistää modbusworker säije
4. hallita sammutus prosessit



### Control loop
yksinketaistettuna
```mermaid
flowchart TD

%%===================
%% blokit
%%=================
sensors["sensors"]
perception["perception"]
state["state"]
decide["decide"]

control["control"]
sleep["time.sleep <br/>CONTROL_LOOP_DT"]

%%====================
%% Loop
%%===================

sensors -->|"sensordata"|perception
perception -->|"perception data"| state

state -->|"RobotState"| decide
decide -->|"command"| control
control --> sleep
sleep --> sensors

```
---