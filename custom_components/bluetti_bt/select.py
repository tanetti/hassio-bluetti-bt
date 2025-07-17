"""Bluetti BT select (enum) entities."""

from __future__ import annotations

import asyncio
import logging
from enum import Enum
import async_timeout

from bleak import BleakError

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_ADDRESS, CONF_NAME, EntityCategory
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .bluetti_bt_lib.base_devices.BluettiDevice import BluettiDevice
from .bluetti_bt_lib.field_attributes import FIELD_ATTRIBUTES, FieldType
from .bluetti_bt_lib.const import WRITE_UUID
from .bluetti_bt_lib.utils.device_builder import build_device
from . import device_info as dev_info, get_unique_id
from .utils import mac_loggable, unique_id_loggable
from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import PollingCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up select entities for Bluetti device."""

    device_name = entry.data.get(CONF_NAME)
    address = entry.data.get(CONF_ADDRESS)

    if not address:
        _LOGGER.error("Device has no address")
        return

    device_info = dev_info(entry)
    bluetti_device = build_device(address, device_name)

    coordinator: PollingCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    selects_to_add = []

    for field_key, field_config in FIELD_ATTRIBUTES.items():
        if (
            bluetti_device.has_field(field_key)
            and field_config.type == FieldType.ENUM and field_config.setter is True
        ):
            selects_to_add.append(
                BluettiSelect(
                    bluetti_device,
                    coordinator,
                    device_info,
                    address,
                    field_key,
                    field_config.name,
                    [option.name for option in field_config.options],
                    entry.entry_id,
                    category=EntityCategory.CONFIG if field_config.setter else None
                )
            )

    async_add_entities(selects_to_add)


class BluettiSelect(CoordinatorEntity, SelectEntity):
    """Bluetti enum (select) entity."""

    def __init__(
        self,
        bluetti_device: BluettiDevice,
        coordinator: PollingCoordinator,
        device_info: DeviceInfo,
        address: str,
        response_key: str,
        name: str,
        options: list[str],
        entry_id: str,
        category: EntityCategory | None = None,
    ):
        """Initialize Bluetti select."""
        super().__init__(coordinator)

        self._bluetti_device = bluetti_device
        self._coordinator = coordinator
        self._client = coordinator.reader.client
        self._polling_lock = coordinator.reader.polling_lock
        e_name = f"{device_info.get('name')} {name}"
        self._address = address
        self._response_key = response_key
        self._options = options
        self._entry_id = entry_id

        self._attr_device_info = device_info
        self._attr_has_entity_name = True
        self._attr_name = name
        self._attr_available = False
        self._attr_unique_id = get_unique_id(e_name)
        self._attr_options = options
        self._attr_entity_category = category
        self._attr_current_option = None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_available

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.reader.persistent_conn and not self.coordinator.reader.client.is_connected:
            self._attr_available = False
            return

        _LOGGER.debug("Updating state of %s", unique_id_loggable(self._attr_unique_id))
        if not isinstance(self.coordinator.data, dict):
            _LOGGER.debug(
                "Invalid data from coordinator (switch.%s)", unique_id_loggable(self._attr_unique_id)
            )
            self._attr_available = False
            self.async_write_ha_state()
            return

        response_data = self.coordinator.data.get(self._response_key)
        if response_data is None:
            self._attr_available = False
            self.async_write_ha_state()
            return

        if not isinstance(response_data, Enum):
            _LOGGER.debug("Expected Enum for %s but got: %s", self._response_key, type(response_data))
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_current_option = response_data.name
        self._attr_available = True
        self.async_write_ha_state()


    async def async_select_option(self, option: str) -> None:
        """Handle selection of a new option from UI."""

        _LOGGER.debug("Turn on %s on %s", self._response_key, mac_loggable(self._address))

        field = FIELD_ATTRIBUTES.get(self._response_key)
        if not field or not hasattr(field, "options") or not field.options:
            _LOGGER.error("Field %s has no valid options", self._response_key)
            return

        # Найти подходящий Enum-класс по значению
        enum_class = None
        for val in field.options:
            if isinstance(val, Enum):
                enum_class = type(val)
                break

        # Если options — просто числа (int), ищем Enum с такими значениями
        if enum_class is None:
            for candidate in Enum.__subclasses__():
                if all(isinstance(v, int) and v in [e.value for e in candidate] for v in field.options):
                    enum_class = candidate
                    break

        if enum_class is None:
            _LOGGER.error("No suitable Enum class found for field %s", self._response_key)
            return

        try:
            enum_value = enum_class[option]  # Преобразуем имя в Enum
        except KeyError:
            _LOGGER.error("Option '%s' not found in Enum %s", option, enum_class)
            return
        
        await self.write_to_device(enum_value.name)


    async def write_to_device(self, option: str):
        """Write to device."""
        command = self._bluetti_device.build_setter_command(self._response_key, option)

        async with self._polling_lock:
            try:
                async with async_timeout.timeout(15):
                    if not self._client.is_connected:
                        await self._client.connect()

                    # Send command
                    _LOGGER.debug("Requesting %s (%s,%s)", command, self._response_key, option)
                    await self._client.write_gatt_char(
                        WRITE_UUID, bytes(command)
                    )

                    # Wait until device has changed value, otherwise reading register might reset it
                    await asyncio.sleep(1)

            except TimeoutError:
                _LOGGER.error("Timed out for device %s", mac_loggable(self._address))
                return None
            except BleakError as err:
                _LOGGER.error("Bleak error: %s", err)
                return None
            finally:
                # Disconnect if connection not persistant
                if not self._coordinator.reader.persistent_conn:
                    await self._client.disconnect()

        await self.coordinator.async_request_refresh()