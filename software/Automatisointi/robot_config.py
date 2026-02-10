
"""
RobotConfig.py

Luonut Tero Nikkola luotu yhdessä ChatGPT-5 mini:n kanssa

Sisältää kaikki robotin parametrit ja raja-arvot, jotka eivät muutu ajon aikana.
"""
import json
import logging
from pathlib import Path
from math import pi
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = Path('robot_config.json')
# yleisiä muuttujia

CONTROL_LOOP_DT = 0.1 # sekunttia
# Ohjelman testaus generoidulla anturi arvoilla
USE_SIMULATION = True

# testi muuttujia joilla voidaan aktivoida laitteita ja testata ohjelmaa jos joitain laitetta ei ole käytössä
MODBUS_AVAILABLE = True
CAMERA_AVAILABLE = os.getenv("CAMERA_AVAILABLE", "0") == "1"
IMU_AVAILABLE = os.getenv("IMU_AVAILABLE", "0") == "1"
IO_AVAILABLE = os.getenv("IO_AVAILABLE", "0") == "1"

CAMERA_URL = os.getenv("CAMERA_URL", "http://localhost:8000/depth")
IO_URL = os.getenv("IO_URL","http://localhost:8000/IO")
IMU_URL = os.getenv("IMU_URL","http://localhost:8000")

# Renkaan koko metreinä
WHEEL_DIAMETER = 0.23  # m


# Esteiden havaitsemisen minimi-etäisyys
OBSTACLE_MIN_DISTANCE = 300  # mm
OBSTACLE_NEAR_DISTANCE = 800 # mm
# Ohjausparametrit



#moottorin speksit
MOTOR_IDS = [1,3,4,6]
PORTSIDE_MOTORS = [1,3] # Kulkusuuntaan katsoen vasemman puoleiset moottorit
STARBOAD_MOTORS = [4,6] # Kulkusuuntaan katsoen oikean puoleiset moottorit
POLES = 20 # moottorin navat
POLE_PARES = POLES/2 #napa parit
RPM_FACTOR = 60 /POLE_PARES 
MAX_PULSES = 165 # moottorin ohjaimen antama maxsimi pulssi arvo keskimääräisesti
GEAR_RATIO = 1/4.5 # moottorin välitys suhde.

# Maksimi kierros nopeus laskettu
MAX_RPS = MAX_PULSES/POLE_PARES* GEAR_RATIO # Välitys suhde huomioitu
MAX_RPM = MAX_RPS*60
# Maksimi nopeus (lineaarinen)
MAX_LINEAR_SPEED = pi*WHEEL_DIAMETER*MAX_RPS  # m/s laskettu
MAX_ANGULAR_SPEED = 3.14  # rad/s arvioitu
MAX_SPEED_VALUE = 1000 # Moottori ohjaimelle annettava max nopeus ohje [0-1000]

_DEFAULT_LINEAR_SPEED = MAX_LINEAR_SPEED*0.30  # m/s
_DEFAULT_ANGULAR_SPEED = MAX_ANGULAR_SPEED*0.3  # rad/s
_DEFAULT_LINEAR_SPEED_BACKWARD = -MAX_LINEAR_SPEED*0.20  # m/s

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


class ChangeableConfig:
    """Luokka, joka pitää sisällään konfiguroitavat parametrit."""
    
    DEFAULT_LINEAR_SPEED = _DEFAULT_LINEAR_SPEED
    DEFAULT_ANGULAR_SPEED = _DEFAULT_ANGULAR_SPEED
    DEFAULT_LINEAR_SPEED_BACKWARD = _DEFAULT_LINEAR_SPEED_BACKWARD


# konfiguraatio jota voidaan muuttaa ajon aikana GUI:n kautta
def load_config():
    """Lataa konfiguraatio tiedoston, jos se on olemassa."""
    
    if not CONFIG_FILE.exists():
        logger.info("No configuration file found, using default settings.")
        return
    
    try:
        with open(CONFIG_FILE) as f:
            config_data = json.load(f)
            ChangeableConfig.DEFAULT_LINEAR_SPEED = float(config_data.get("DEFAULT_LINEAR_SPEED", _DEFAULT_LINEAR_SPEED))
            ChangeableConfig.DEFAULT_ANGULAR_SPEED = float(config_data.get("DEFAULT_ANGULAR_SPEED", _DEFAULT_ANGULAR_SPEED))
            ChangeableConfig.DEFAULT_LINEAR_SPEED_BACKWARD = float(config_data.get("DEFAULT_LINEAR_SPEED_BACKWARD", _DEFAULT_LINEAR_SPEED_BACKWARD))
            logger.info("Configuration loaded from robot_config.json")
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
def reload_config():
    """Lataa konfiguraatio tiedoston uudestaan."""
    load_config()
    logger.info("Configuration reloaded.")


load_config()