
"""
RobotConfig.py
Luonut Tero Nikkola luotu yhdessä Chat gpt:n kanssa

Sisältää kaikki robotin parametrit ja raja-arvot, jotka eivät muutu ajon aikana.
"""
from math import pi
# yleisiä muuttujia

CONTROL_LOOP_DT = 0.1
# Ohjelman testaus generoidulla anturi arvoilla
USE_SIMULATION = True

# testi muuttujia joilla voidaan aktivoida laitteita ja testata ohjelmaa jos joitain laitetta ei ole käytössä
MODBUS_AVAILABLE = True
IMU_AVABLE = False
CAMERA_AVABLE = False
IO_AVABLE = False

# Renkaan koko metreinä
WHEEL_DIAMETER = 0.26  # m


# Esteiden havaitsemisen minimi-etäisyys
OBSTACLE_MIN_DISTANCE = 300  # mm
OBSTACLE_NEAR_DISTANCE = 800 # mm
# Ohjausparametrit



#moottorin speksit
MOTOR_IDS = [1,3,4,6]
POLES = 30 # moottorin navat
POLE_PARES = POLES/2 #napa parit
RPM_FACTOR = 60 /POLE_PARES 
MAX_PULSES = 165 # moottorin ohjaimen antama maxsimi pulssi arvo

# Maksimi kierros nopeus laskettu
MAX_RPS = MAX_PULSES/POLE_PARES
MAX_RPM = MAX_RPS*60
# Maksimi nopeus (lineaarinen)
MAX_LINEAR_SPEED = pi*WHEEL_DIAMETER*MAX_RPS  # m/s laskettu
MAX_ANGULAR_SPEED = 3.14  # rad/s arvioitu
MAX_SPEED_VALUE = 1000 # Moottori ohjaimelle annettava max nopeus ohje [0-1000]

DEFAULT_LINEAR_SPEED = MAX_LINEAR_SPEED*0.20  # m/s
DEFAULT_ANGULAR_SPEED = MAX_ANGULAR_SPEED*0.5  # rad/s

# Debug asetukset Jos haluat nähdä debug tietoa konsolissa, aseta arvo True
DEBUG_MAIN = False  # Tulostetaanko main moduulin tiedot konsoliin
DEBUG_SENSOR_VALUES = False  # Tulostetaanko anturi arvot konsoliin
DEBUG_PERCEPTION = False  # Tulostetaanko havaitut tilat konsoliin
DEBUG_CONTROL_COMMANDS = False  # Tulostetaanko ohjaus käskyt konsoliin 
DEBUG_STATE_CHANGES = False  # Tulostetaanko tilamuutokset konsoliin    
DEBUG_DECISIONS = False  # Tulostetaanko päätökset konsoliin
DEBUG_MODBUS = False  # Tulostetaanko Modbus viestit konsoliin
DEBUG_CONTOL_LOOP = False  # Tulostetaanko ohjaus silmukan suoritukset konsoliin
# GUI Debug asetukset


DEBUG_APP = False  # Tulostetaanko GUI sovelluksen tapahtumat konsoliin
DEBUG_DASHBOARD = False  # Tulostetaanko dashboardin päivitykset konsoliin
DEBUG_GUI_CONTROL = False  # Tulostetaanko GUI ohjaus tapahtumat konsoliin
