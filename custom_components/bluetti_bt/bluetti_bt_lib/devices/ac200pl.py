"""AC200PL fields."""

from typing import List

from ..field_enums import ChargingMode
# from ..field_enums import ChargingMode, AutoSleepMode, UpsMode, EcoShutdown
from ..utils.commands import ReadHoldingRegisters
from ..base_devices.ProtocolV1Device import ProtocolV1Device

class AC200PL(ProtocolV1Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC200PL", sn)

        # Power IO
        # self.struct.add_decimal_field("internal_ac_voltage", 71, 1, multiplier=10)
        # self.struct.add_decimal_field("internal_ac_frequency", 74, 2, multiplier=10)
        # self.struct.add_decimal_field('ac_input_voltage', 77, 1)
        # self.struct.add_decimal_field('ac_input_frequency', 80, 2, multiplier=10)
        
        # Battery packs
        self.struct.add_uint_field("pack_num_max", 91)  # internal
        # self.struct.add_decimal_field("total_battery_voltage", 92, 1)
        self.struct.add_uint_field("pack_num_result", 96)  # internal
        # self.struct.add_decimal_field("pack_voltage", 98, 2)  # Full pack voltage
        self.struct.add_uint_field("pack_battery_percent", 99)
        # self.struct.add_decimal_array_field("cell_voltages", 105, 16, 2)  # internal
        # self.struct.add_version_field("pack_bms_version", 201)

        # Controls (3000)
        # self.struct.add_enum_field('ups_mode', 3001, UpsMode)
        # self.struct.add_bool_field('ac_output_on', 3007)
        # self.struct.add_bool_field('dc_output_on', 3008)
        # self.struct.add_bool_field('grid_charge_on', 3011)
        # self.struct.add_bool_field('time_control_on', 3013)
        # self.struct.add_uint_field('battery_range_start', 3015)
        # self.struct.add_uint_field('battery_range_end', 3016)
        # self.struct.add_uint_field('max_grid_charge_current', 3019)
        # 3031-3033 is the current device time & date without a timezone
        # self.struct.add_bool_field('bluetooth_connected', 3036)
        # 3039-3056 is the time control programming
        self.struct.add_bool_field('power_off', 3060)
        # self.struct.add_enum_field('auto_sleep_mode', 3061, AutoSleepMode)
        # self.struct.add_bool_field('silent_charging_on', 3065)
        # self.struct.add_enum_field('eco_shutdown', 3064, EcoShutdown)
        self.struct.add_enum_field('charging_mode', 3065, ChargingMode)
        # self.struct.add_bool_field('power_lifting_on', 3066)
        
    @property
    def pack_num_max(self):
        return 2

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return super().polling_commands + [
            ReadHoldingRegisters(3060, 1),
            ReadHoldingRegisters(3065, 1),
        ]

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        return [
            ReadHoldingRegisters(91, 1),
            ReadHoldingRegisters(99, 1),
        ]

    @property
    def writable_ranges(self) -> List[range]:
        return super().writable_ranges + [range(3060, 3061)] + [range(3065, 3066)]
        