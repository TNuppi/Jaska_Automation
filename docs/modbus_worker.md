# modbus_worker.py

Moduulin tehtävänä on kerätä modbus väylään lähetettävät komennot yhteen ja hoitaa niitä omassa säikeessä. Moduulissa pyritään priorisoimaan kirjoitus käskyt ensisijaisiksi. 

## Riippuvuus ohjelma kokonaisuudessa
```mermaid
flowchart TD

sensors["sensors.py"]
control["control.py"]
driver["ModbusDriver.py"]
worker["modbus_worker.py"]

driver <-- data <br/> read/write --> worker
worker -- read --> sensors
control -- write --> worker

```

## Koodin toiminta periaate

```mermaid
flowchart TD
    %% ========= ALUSTUS =========
    createWorker(["ModbusWorker __init__()"])

    initVars["Alusta:<br/>poll_interval<br/>running = False<br/>motor_status<br/>lock<br/>commands = []"]

    %% ========= THREAD =========
    startThread(["Thread start()"])
    runMethod(["run()"])

    setRunning["running = True"]

    mainLoop{"running == True?"}

    acquireLock["lock.acquire()"]

    %% ========= KOMENTOJONO =========
    hasCommands{"commands not empty?"}

    popCommand["pop command<br/>(cmd, motor_id, value)"]

    isSetSpeed{"cmd == set_speed?"}
    isSetDirection{"cmd == set_direction?"}

    setSpeed["modbus.set_speed()"]
    setDirection["modbus.set_direction()"]

    %% ========= STATUS =========
    readStatus["Lue moottorien status<br/>for mid in MOTOR_IDS"]

    updateStatus["Päivitä motor_status[mid]"]

    releaseLock["lock.release()"]

    sleepInterval["sleep(poll_interval)"]

    %% ========= ULKOISET METODIT =========
    stopAll["stop_all()"]
    stopAllAction["running = False<br/>modbus STOP ALL"]

    emergencyStop["emergency_stop()"]
    emergencyAction["modbus.emergency_stop()"]

    enqueueSpeed["enqueue_set_speed()"]
    enqueueDirection["enqueue_set_direction()"]

    getStatus["get_status(motor_id)"]

    %% ========= VIRTAUS =========
    createWorker --> initVars --> startThread --> runMethod
    runMethod --> setRunning --> mainLoop

    mainLoop -- Kyllä --> acquireLock --> hasCommands

    hasCommands -- Kyllä --> popCommand --> isSetSpeed
    
    isSetSpeed -- Ei --> isSetDirection
    isSetSpeed -- Kyllä --> setSpeed 
    
    
    isSetDirection -- Kyllä --> setDirection
    
    hasCommands -- Ei --> readStatus --> updateStatus --> releaseLock --> sleepInterval --> mainLoop

    mainLoop -- Ei --> stopAll

    %% ========= ULKOISET KUTSUT =========
    enqueueSpeed --> acquireLock
    enqueueDirection --> acquireLock

    stopAll --> stopAllAction
    emergencyStop --> emergencyAction
    getStatus --> acquireLock


```
