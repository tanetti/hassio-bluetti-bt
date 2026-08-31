from ..base_devices import BaseDeviceV1
from ..fields import (
    FieldName,
    EnumField,
    DecimalField,
    SwitchField,
    SelectField,
    UIntField,
    VersionField
)
from ..enums import ChargingMode, BatteryState


class AC200PL(BaseDeviceV1):
    def __init__(self):
        super().__init__(
            [
                DecimalField(FieldName.INTERNAL_AC_VOLTAGE, 71, 1, 10),
                SwitchField(FieldName.CTRL_AC, 3007),
                SwitchField(FieldName.CTRL_DC, 3008),
                SwitchField(FieldName.CTRL_POWER_OFF, 3060),
                SelectField(FieldName.CTRL_CHARGING_MODE, 3065, ChargingMode),
            ],
            [
                UIntField(FieldName.PACK_SELECTED, 96),
                UIntField(FieldName.PACK_BATTERY_SOC, 99),
                EnumField(FieldName.PACK_BATTERY_STATE, 100, BatteryState),
                VersionField(FieldName.VER_BMS, 201),
            ],
            max_packs=3,
        )
