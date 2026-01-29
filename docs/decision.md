# decision.py

Moduulin tehtävänä on tehdä päätökset statuksen mukaan ja välittää ohjauskäskyt controlliin.
Moduuli sisltää tilakoneet ja häiriön käsittelyn.

```mermaid
flowchart TD

types["robot_type.py"]
config["robot_config.py"]
decision["desision.py"]
data["return: </br> ControlCommand "]
state["state.py"]
gui["GUI"]

types -->|ControlCommand| decision
types -->|PerceptionData| decision
config -->|settings| decision
state <-->|RobotStateData| decision
gui --> decision 
decision --> data

classDef datastyle fill:#4EC9B0,stroke:#333,stroke-width:2px
class data datastyle

```
---
## Funktiot
###  decide(perception: PerceptionData) -> ControlCommand:
Moduulin "pääfunktio" jonka tarkoitus on toimia tilakoneena jota käytetään mainissa.
Funktio lukee perception datan ja tarkkailee missä tilassa robotti on ja sen mukaan muuttaa robotin tilaa ja antaa ohjaus käskyjä. 

#### Vuokaavio
(yksinkertaistettu)

```mermaid
flowchart TD
    decideStart(["decide(perception)"])

    emergencyCheck{"Hätäpysäytys<br/>aktiivinen?"}
    resetCheck{"Virhetila &<br/>reset-napin reuna?"}

    errorState{"status == ERROR?"}
    okRecovery{"Palautuminen<br/>OK-tilaan"}

    manualMode{"control_type == MAN?"}
    autoMode{"control_type == AUTO?"}

    manualControl["(MAN)<br/>Käsiohjaus<br/>MAN_FORWARD <br/>MAN_BACKWARD<br/>MAN_LEFT<br/>MAN_RIGHT<br/>STOP"]
    autoControl["(AUTO)<br/>Automaattiohjaus<br/>STOP<br/>FORWARD <br/>SLOW_FORWARD<br/>AVOIDING<br/>DRIVE_DISTANCE<br/>WAIT"]

    handleError["Virheenkäsittely"]
    stopAll["STOP"]

    decideStart --> emergencyCheck

    emergencyCheck -- Kyllä --> stopAll
    emergencyCheck -- Ei --> resetCheck

    resetCheck -- Kyllä --> okRecovery --> manualMode
    resetCheck -- Ei --> errorState

    errorState -- Kyllä --> handleError
    errorState -- Ei --> manualMode

    manualMode -- Kyllä --> manualControl
    manualMode -- Ei --> autoMode
    
    autoMode -- Kyllä --> autoControl
    autoMode -- Ei --> errorState
    
    handleError --> stopAll
    
```

---
### Command funktiot

Funktiot päivittää halutun lineaari- ja kulmanopeuden (m/s & rad/s) ControlData objektiin joka käsitellään control.py:ssä. 

```mermaid

flowchart TD
    controlCommandStart(["ControlCommand functions"])

    selectCommand{"Funktio?"}

    stopCmd["stop():<br/>linear_speed=0.0<br/>angular_speed=0.0"]
    forwardCmd["drive_forward():<br/>linear_speed=DEFAULT_LINEAR_SPEED<br/>angular_speed=0.0"]
    slowForwardCmd["drive_slow_forward():<br/>linear_speed=0.5*DEFAULT_LINEAR_SPEED<br/>angular_speed=0.0"]
    backwardCmd["drive_backward():<br/>linear_speed=DEFAULT_LINEAR_SPEED_BACKWARD<br/>angular_speed=0.0"]
    turnLeftCmd["turn_left():<br/>linear_speed=0.0<br/>angular_speed=DEFAULT_ANGULAR_SPEED"]
    turnRightCmd["turn_right():<br/>linear_speed=0.0<br/>angular_speed=-DEFAULT_ANGULAR_SPEED"]
    turnCmd["turn():<br/>linear_speed=0.5*DEFAULT_LINEAR_SPEED<br/>angular_speed=DEFAULT_ANGULAR_SPEED"]

    %% ===== Virtaus =====
    controlCommandStart --> selectCommand

    selectCommand -- "STOP" --> stopCmd
    selectCommand -- "FORWARD" --> forwardCmd
    selectCommand -- "SLOW_FORWARD" --> slowForwardCmd
    selectCommand -- "BACKWARD" --> backwardCmd
    selectCommand -- "TURN_LEFT" --> turnLeftCmd
    selectCommand -- "TURN_RIGHT" --> turnRightCmd
    selectCommand -- "TURN" --> turnCmd


```

---
### Häiriön käsittely
Tähän funktioon voidaan laittaa erillaisia häiriön käsittelyyn liittyviä toimintoja, tällä hetkellä logaa errorin jos se ei ole sitä vielä tehnyt.
 
```mermaid
flowchart TD
    handleErrorStart(["handle_error()"])

    readRobotState["get_state()<br/>robot_states"]

    wasAlreadyInError{"last_status == 'ERROR'?"}

    logErrorAndUpdate["log error<br/>update_state:<br/>last_status=ERROR"]

    stopCommand["return stop()"]

    handleErrorStart --> readRobotState --> wasAlreadyInError

    wasAlreadyInError -- Ei --> logErrorAndUpdate --> stopCommand
    wasAlreadyInError -- Kyllä --> stopCommand

```
---
### Manuaali ohjaukset
Funktioilla voidaan ohjata robottia vakio nopeuksilla eteen, taakse ja käännökset oikealle ja vasemmalle. Eteenpäin ohjaukseen on tehty rajoitukset että jos este on lähellä niin ajetaan hitaasti jos este on edessä niin estetään liike eteenpäin. 
```mermaid

flowchart TD
    manualHandlerStart(["Manual control handler"])

    selectMotion{"control_type == MAN?"}

    %% --- FORWARD ---
    checkObstacleNear{"Este lähellä<br/>mutta ei edessä?"}
    slowForward["drive_slow_forward()"]

    checkObstacleFront{"Este edessä?"}
    stopMotion["stop()"]
    forwardMotion["drive_forward()"]

    %% --- MUUT SUUNNAT ---
    backwardMotion["drive_backward()"]
    turnLeftMotion["turn_left()"]
    turnRightMotion["turn_right()"]

    %% --- VIRTAUS ---
    manualHandlerStart --> selectMotion

    selectMotion -- "MAN_FORWARD" --> checkObstacleNear
    checkObstacleNear -- Kyllä --> slowForward
    checkObstacleNear -- Ei --> checkObstacleFront

    checkObstacleFront -- Kyllä --> stopMotion
    checkObstacleFront -- Ei --> forwardMotion

    selectMotion -- "MAN_BACKWARD" --> backwardMotion
    selectMotion -- "MAN_LEFT" --> turnLeftMotion
    selectMotion -- "MAN_RIGHT" --> turnRightMotion

```

---

### Automaatti tilat

#### eteenpäin ajo

Funktiossa robottia ohjataan eteen päin jos ei ole esteitä, jos este on lähellä niin hidastetaan ja jos este on edesä niin jäädään odottamaan.
```mermaid
flowchart TD
    handleForwardStart(["handle_forward(perception)"])

    readRobotState["get_state()"]

    obstacleNear{"obstacle_near?"}
    setSlowForward["update_state:<br/>motion=SLOW_FORWARD<br/>last_motion=state.motion"]
    stopCommand["return stop()"]

    obstacleFront{"obstacle_front?"}
    setWaitState["update_state:<br/>motion=WAIT<br/>last_motion=state.motion"]
    slowForwardCommand["return drive_slow_forward()"]

    forwardCommand["return drive_forward()"]

    handleForwardStart --> readRobotState --> obstacleNear

    obstacleNear -- Kyllä --> setSlowForward --> stopCommand
    obstacleNear -- Ei --> obstacleFront

    obstacleFront -- Kyllä --> setWaitState --> slowForwardCommand
    obstacleFront -- Ei --> forwardCommand

```
---

#### eteen ajo hitaasti

Funktiossa ajetaan hitaasti eteenpäin jos este on lähellä. Jos taas este on suoraan edessä niin pysähdytään odottamaan että este poistuu. Jos este poistuu edestä niin jatketaan edellistä tilaa. 

Huom! tarkista että paluu ei mene WAIT tilaan esteiden poistuessa. 

```mermaid
flowchart TD
    handleSlowForwardStart(["handle_slow_forward(perception)"])

    readRobotState["get_state()"]

    obstacleNear{"obstacle_near?"}
    restorePreviousMotion["update_state:<br/>motion=state.last_motion<br/>last_motion=state.motion"]
    slowForwardCommand["return drive_slow_forward()"]

    obstacleFront{"obstacle_front?"}
    setWaitState["update_state:<br/>motion=WAIT<br/>last_motion=state.motion"]
    stopCommand["return stop()"]

    handleSlowForwardStart --> readRobotState --> obstacleNear

    obstacleNear -- Ei --> restorePreviousMotion --> slowForwardCommand
    obstacleNear -- Kyllä --> obstacleFront

    obstacleFront -- Kyllä --> setWaitState --> stopCommand
    obstacleFront -- Ei --> slowForwardCommand


```
---

#### matka ajo

funktio suorittaa tällähetkellä tehtävän että alkaa kulkemaan tavoite matkan eteen päin ja pysähtyy siihen. 

HUOM! Tällä hetkellä viiveen ja pysäytys ramppien takia matka etenee yli tavoite matkan. 

```mermaid
flowchart TD
    handleDriveDistanceStart(["handle_drive_distance(perception)"])

    readDistanceInfo["get_distance_info()<br/>start, target, travelled"]
    readRobotState["get_state()"]

    targetMissing{"target is None?"}
    stopNoTarget["log error<br/>update_state:<br/>motion=STOP<br/>target_distance=0.0"]
    stopCommand1["return stop()"]

    targetReached{"travelled ≥ target?"}
    stopAtTarget["log info<br/>update_state:<br/>motion=STOP<br/>start_distance=travelled"]
    stopCommand2["return stop()"]

    obstacleNearOnly{"obstacle_near<br/>and not obstacle_front?"}
    ensureSlowForward["update_state:<br/>last_motion='SLOW FORWARD'<br/>(if needed)"]
    slowForwardCommand["return drive_slow_forward()"]

    obstacleFront{"obstacle_front?"}
    setWaitState["update_state:<br/>motion=WAIT<br/>last_motion=state.motion"]
    stopCommand3["return stop()"]

    forwardCommand["return drive_forward()"]

    %% ===== Virtaus =====
    handleDriveDistanceStart --> readDistanceInfo --> readRobotState --> targetMissing

    targetMissing -- Kyllä --> stopNoTarget --> stopCommand1
    targetMissing -- Ei --> targetReached

    targetReached -- Kyllä --> stopAtTarget --> stopCommand2
    targetReached -- Ei --> obstacleNearOnly

    obstacleNearOnly -- Kyllä --> ensureSlowForward --> slowForwardCommand
    obstacleNearOnly -- Ei --> obstacleFront

    obstacleFront -- Kyllä --> setWaitState --> stopCommand3
    obstacleFront -- Ei --> forwardCommand


```
---

#### Wait käsittely
Waitin tarkoituksena on tällähetkellä että jos kohde on liian lähellä tai kameran syvyys näön ollessa käytössä syvyyttä ei saada niin automaatti tilassa robotti pysähtyy ja jää odottamaan että este poistuu kunnes kykenee jatkamaan edellistä tehtävää.
```mermaid

flowchart TD
    handleWaitStart(["handle_wait(perception)"])

    obstacleFront{"obstacle_front?"}

    waitStop["return stop()"]

    readRobotState["get_state()"]
    determinePreviousMotion["previous_motion = last_motion or 'STOP'"]
    restoreMotion["update_state:<br/>motion = previous_motion"]

    prevDriveDistance{"previous_motion == DRIVE_DISTANCE?"}
    driveDistanceSlow["return drive_slow_forward()"]

    prevForward{"previous_motion == FORWARD?"}
    driveForwardCmd["return drive_forward()"]

    prevSlowForward{"previous_motion == SLOW_FORWARD?"}
    driveSlowForwardCmd["return drive_slow_forward()"]

    prevAvoiding{"previous_motion == AVOIDING?"}
    turnCmd["return turn()"]

    prevStop{"previous_motion == STOP?"}
    stopCmd["return stop()"]

    %% ===== Virtaus =====
    handleWaitStart --> obstacleFront

    obstacleFront -- Kyllä --> waitStop
    obstacleFront -- Ei --> readRobotState --> determinePreviousMotion --> restoreMotion

    restoreMotion --> prevDriveDistance
    prevDriveDistance -- Kyllä --> driveDistanceSlow
    prevDriveDistance -- Ei --> prevForward

    prevForward -- Kyllä --> driveForwardCmd
    prevForward -- Ei --> prevSlowForward

    prevSlowForward -- Kyllä --> driveSlowForwardCmd
    prevSlowForward -- Ei --> prevAvoiding

    prevAvoiding -- Kyllä --> turnCmd
    prevAvoiding -- Ei --> prevStop

    prevStop -- Kyllä --> stopCmd
    prevStop -- Ei --> stopCmd


```

---

### Gui Helpperit

Gui helpperit ovat käytössä, koska oli ongelmia komentojen statuksen päivityksessä suoraan guissa, mutta nämä voi jatkossa siirtää pois. niin että gui tekee suoraan statuksen päivityksen.
```mermaid

flowchart TD
    guiAction(["GUI action"])

    selectGuiCommand{"GUI-pyyntö?"}

    %% --- TILAN VAIHTO ---
    setManualMode["update_state:<br/>control_type=MAN<br/>motion=STOP"]
    setAutoMode["update_state:<br/>control_type=AUTO<br/>motion=STOP"]

    %% --- YLEINEN STOP ---
    guiStop["update_state:<br/>motion=STOP"]

    %% --- MANUAL-LIIKKEET ---
    manForward["update_state:<br/>motion=MAN_FORWARD"]
    manBackward["update_state:<br/>motion=MAN_BACKWARD"]
    manLeft["update_state:<br/>motion=MAN_LEFT"]
    manRight["update_state:<br/>motion=MAN_RIGHT"]

    %% ===== VIRTAUS =====
    guiAction --> selectGuiCommand

    selectGuiCommand -- "SET MANUAL" --> setManualMode
    selectGuiCommand -- "SET AUTO" --> setAutoMode

    selectGuiCommand -- "STOP" --> guiStop

    selectGuiCommand -- "MAN_FORWARD" --> manForward
    selectGuiCommand -- "MAN_BACKWARD" --> manBackward
    selectGuiCommand -- "MAN_LEFT" --> manLeft
    selectGuiCommand -- "MAN_RIGHT" --> manRight

```