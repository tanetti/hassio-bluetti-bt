"""AC200PL fields."""

from typing import List

# from ..field_enums import ChargingMode, AutoSleepMode, UpsMode
from ..utils.commands import ReadHoldingRegisters
from ..base_devices.ProtocolV2Device import ProtocolV2Device

class AC200PL(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC200PL", sn)

        # Power IO
        # self.struct.add_sn_field('serial_number', 17)
        # self.struct.add_version_field('arm_version', 23)
        # self.struct.add_version_field('dsp_version', 25)
        self.struct.add_uint_field('dc_input_power', 36)
        self.struct.add_uint_field('ac_input_power', 37)
        self.struct.add_uint_field('ac_output_power', 38)
        self.struct.add_uint_field('dc_output_power', 39)
        # self.struct.add_decimal_field('power_generation', 41, 1)  # Total power generated since last reset (kwh)
        self.struct.add_uint_field('total_battery_percent', 43)
        # self.struct.add_bool_field('ac_output_on', 48)
        # self.struct.add_bool_field('dc_output_on', 49)
        self.struct.add_decimal_field('ac_input_voltage', 77, 1)
        # self.struct.add_decimal_field('ac_input_frequency', 80, 2)

        # Controls (3000)
        # self.struct.add_enum_field('ups_mode', 3001, UpsMode)
        # self.struct.add_bool_field('split_phase_on', 3004)
        # self.struct.add_enum_field('split_phase_machine_mode', 3005, MachineAddress)
        # self.struct.add_uint_field('pack_num', 3006)
        # self.struct.add_bool_field('ac_output_on', 3007)
        # self.struct.add_bool_field('dc_output_on', 3008)
        self.struct.add_bool_field('ac_output_on_switch', 3007)
        self.struct.add_bool_field('dc_output_on_switch', 3008)
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
        self.struct.add_bool_field('silent_charging_on', 3065)
        # self.struct.add_enum_field('charging_mode', 3065, ChargingMode)
        self.struct.add_bool_field('power_lifting_on', 3066)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return super().polling_commands + [
            ReadHoldingRegisters(10, 40),
            ReadHoldingRegisters(70, 21),
            ReadHoldingRegisters(3001, 66),
        ]

    @property
    def writable_ranges(self) -> List[range]:
        return super().writable_ranges + [range(3000, 3067)]