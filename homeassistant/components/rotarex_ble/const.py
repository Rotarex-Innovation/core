"""Constants for the Rotarex DIMES SRG Bluetooth integration."""

from rotarex_dimes_ble import Region, TankType

DOMAIN = "rotarex_ble"

CONF_TANK_TYPE = "tank_type"

DEFAULT_REGION = Region.EUROPE
DEFAULT_TANK_TYPE = TankType.CAMPING_CYLINDER

# The tank types offered in the ROTAREX DIMES app
TANK_TYPES = [TankType.CAMPING_CYLINDER, TankType.CAMPING_SMART, TankType.CAMPING_TANK]
