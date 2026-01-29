# control.py

Moduulin tarkoituksena on ottaa vastaan ohjauskäskyt, muuttaa ne moottorin ohjauskorteille sopiviin muotoihin ja lähettää ne modbusworkerille eteenpäin.

```mermaid
flowchart TD

types["robot_types.py"]
config["robot_config.py"]
control["control.py"]
worker["modbus_worker.py"]


types -->|ControlComand| control
config -->|settings| control

control -->|direction/speed| worker

```

## Funktiot

### apply_control(command: ControlCommand | None):

Modulin pääfunktio jota käytetään mainissa olevaas control loopissa. Funktion tarkoituksena on lähettää käskyt moottoreille jos ohjaus käsky on muuttunut. Moottorin nopeudet rajataan niin että nopeus ohjeet eivät voi ylittää maksimi arvoja. 

```mermaid
flowchart TD
    startApplyControl(["apply_control(command)"])

    commandIsNone{"command is None?"}
    stopAllMotors["modbus_worker.stop_all()<br/>_last_command = None"]
    returnAfterStop["return"]

    sameAsLast{"command == _last_command?"}
    returnNoChange["return"]

    storeLast["_last_command = command"]

    limitLinear["Clamp linear_speed<br/>±MAX_LINEAR_SPEED"]
    limitAngular["Clamp angular_speed<br/>±MAX_ANGULAR_SPEED"]

    calculateSpeeds["calculate_motor_speeds(linear, angular)"]
    sendMotors["send_to_motors(motor_speeds)"]

    %% ===== Virtaus =====
    startApplyControl --> commandIsNone

    commandIsNone -- Kyllä --> stopAllMotors --> returnAfterStop
    commandIsNone -- Ei --> sameAsLast

    sameAsLast -- Kyllä --> returnNoChange
    sameAsLast -- Ei --> storeLast

    storeLast --> limitLinear --> limitAngular
    limitAngular --> calculateSpeeds --> sendMotors


```

### calculate_motor_speeds(linear: float, angular: float) -> dict[int, int]:

Funktion tarkoituksena on laskea moottori kohtaiset nopeudet lineaari ja kulmanopeuksista. 
ja palauttaa moottorikohtaisen dictionaryn jossa on moottori kohtaiset nopeusohjeet.

#### Vuokaavio
```mermaid
flowchart TD
    startCalc(["calculate_motor_speeds(linear, angular)"])

    normalizeLinear["Lineaari nopeuden normalisointi"]
    normalizeAngular["Kulma nopeuden normalisointi"]

    motorCalc["Laske moottori kohtaiset nopeudet"]

    scaleSpeeds["muunna int-arvoiksi"]

    returnDict["return {<br/>1, 3, 4, 6 : nopeus<br/>}"]

    %% ===== Virtaus =====
    startCalc --> normalizeLinear
    normalizeLinear --> normalizeAngular
    normalizeAngular --> motorCalc
    motorCalc --> scaleSpeeds
    scaleSpeeds --> returnDict



```

#### Nopeuksien normalisointi

nopeudet normalisoidaan kaavalla $$ v_{norm} = \frac {v}{v_{max}} $$

jossa

$v_{norm} = $ normalisoitu lineaari- tai kulmanopeus
$v =  $ lineaari- tai kulmanopeus ohje
$v_{max}= $ lineaari tai kulmanopeuden maximi (MAX_LINEAR_SPEED, MAX_ANGULAR_SPEED) arvo joka on määritelty robot_confic.py moduulissa.

Jos maks arvot ei ole saatavilla niin normalisoiduksi arvoksi määritetään 0.0

#### moottori kohtaisen nopeuden laskenta

Paarpuurin puoleiset moottorit lasketaan kaavalla $$C_P=(v_{norm_{L}}-v_{norm_{A}})\cdot C_{max} $$

ja styyrpuurin puoleiset lasketaan kaavalla $$C_S=(v_{norm_{L}}+v_{norm_{A}})\cdot C_{max} $$

jossa

$C_P$ = paarpuurin puoleisten moottorien ohjauskomento

$C_S$ = styyrpuurin puoleisten moottorien ohjauskomento

$v_{norm_{L}} $ = normalisoitu lineaarinen nopeus

$v_{norm_{A}} $ = normalisoitu kulmanopeus

$C_{max} $ = moottoriohjaimelle annettavan nopeuskomennon maksimiarvo
(vastaa MAX_SPEED_VALUE-vakioita, määritelty robot_config.py-moduulissa) 

##### Havaittu rajoite

Mikäli sekä lineaarinen että kulmanopeus saavuttavat maksimiarvonsa samanaikaisesti, voi moottorikohtainen ohjauskomento ylittää sallitun maksimiarvon 
$C_{max}$ esim⁡. $$v_{norm_{L}}=1, \quad v_{norm_{A}}=1 $$
joka johtaa tulokseen $$C_S= 2 \cdot C{max} $$
Tällöin ohjausarvo joudutaan rajaamaan moottoriohjaimen tai alempien ohjelmistokerrosten toimesta, mikä voi aiheuttaa liikkeen suunnan vääristymistä äärimmäisissä ohjaustilanteissa.

##### Vaikutus järjestelmän toimintaan

Käytännössä järjestelmä toimii turvallisesti, sillä:

* yksittäiset nopeuskomennot rajataan
* moottoriohjaimet eivät hyväksy arvoja yli sallittujen rajojen

Kuitenkin:
* lineaarisuuden säilyminen ei ole taattu
* kaarreliike voi vääristyä maksimiarvojen läheisyydessä

##### Kehitysehdotus

Jatkokehityksessä ohjauskomennot voidaan skaalata yhteisesti siten, että suurin moottorikohtainen arvo ei ylitä sallittua rajaa.

Yksi yleinen ratkaisu on yhteinen skaalaus: $$m = max(|v_L + v_A|, \: |v_L-v_A|) $$
mikäli $m>1$, molemmat arvot skaalataan: $$v_{L}'=\frac {v_L}{m}, \quad v_A' =\frac {v_A}{m} $$
Tämän jälkeen moottorikohtaiset ohjauskomennot lasketaan käyttäen skaalattuja arvoja.

Tämä menetelmä säilyttää liikesuunnan ja estää ohjausarvojen yliohjauksen.

### send_to_motors(motor_vals: dict[int, int]):

Funktion tarkoituksena on käyttää lähettää suunta ja nopeus ohjeet modbus_workkerille. Funktio saa dictionaryn jossa on moottorin nopeus ohje merkillisenä. Se käyttää funktiota speed_to_direction() jossa erotellaan itse nopeus ohje ja suunta omaksi arvoksi, tämän jälkeen suunta ja nopeus lähetetään modbus_workerille.

#### Vuokaavio
```mermaid
flowchart TD
    startSendMotors(["send_to_motors(motor_vals)"])

    tryBlock["try"]

    loopMotors{"Käy dictionary läpi <br/>(motor_id, signed_speed)<br/>Seuraava?"}

    convertSpeed["speed_to_direction(signed_speed)<br/>→ direction, speed"]

    modbusAvailable{"MODBUS_AVAILABLE?"}

    enqueueDirection["enqueue_set_direction(motor_id, direction)"]
    enqueueSpeed["enqueue_set_speed(motor_id, speed)"]

    simulationLog["Loggaa simulointi:<br/>Motor ID, speed, direction"]

    endLoop["Kaikki moottorit käsitelty"]

    exceptionBlock["except Exception"]
    logException["logger.exception:<br/>Failed to send motor commands"]

    %% ===== Virtaus =====
    startSendMotors --> tryBlock --> loopMotors

    loopMotors -- Kyllä --> convertSpeed --> modbusAvailable

    modbusAvailable -- Kyllä --> enqueueDirection --> enqueueSpeed
    modbusAvailable -- Ei --> simulationLog

    loopMotors -- Ei --> endLoop

    tryBlock -. Virhe .-> exceptionBlock --> logException
```
### speed_to_direction(speed: int) -> tuple[int, int]

Funktio muuttaa etumerkillisen nopeuden (±) suunnaksi ja nopeudeksi. Jos nopeus on positiivista suunnaksi määritellään 0 (eteen) jos negatiivista niin 1 (taakse). 
funktio palauttaa suunnan ja nopeuden absoluuttisen arvon. 

### emergency_stop():
Jos MODBUS_AVAILABLE niin nollataan viimeinen käsky ja suoritetaan modbus_worker.emergency_stop() funktio joka lähettää kaikille moottoreille pysäytys käskyn ja pois poistaa moottorit käytöstä. 

***Huom!**: Käytä harkiten moottorien käyttöön palauttaminen voi vaatia koko järjestelmän uudelleen käynnistystä.

### stop_all_motors():

Funktion tarkoituksena on lähettää pysäytys käsky kaikille moottoreille modbus_workeriin.