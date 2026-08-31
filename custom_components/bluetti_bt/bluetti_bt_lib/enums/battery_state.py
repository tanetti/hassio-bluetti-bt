from enum import Enum, unique


@unique
class BatteryState(Enum):
    STANDBY = 0
    CHARGE = 1
    DISCHARGE = 2
