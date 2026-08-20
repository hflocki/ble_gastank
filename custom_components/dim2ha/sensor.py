"""Sensor platform for DIM2HA BLE Integration."""

from __future__ import annotations

import logging
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.match import BluetoothCallbackMatcher
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ble_gastank"
COMPANY_ID = 0xFFFF


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ble_gastank sensors from config entry."""
    mac_address = entry.data["mac_address"].upper()
    tank_capacity = float(entry.data.get("tank_capacity", 22.0))
    fill_stop_percent = float(entry.data.get("fill_stop_percent", 80.0))

    # Erstelle die 3 geforderten Sensoren
    battery_sensor = GasBatterySensor(mac_address)
    percent_sensor = GasPercentSensor(mac_address, fill_stop_percent)
    liter_sensor = GasLiterSensor(mac_address, tank_capacity, fill_stop_percent)

    async_add_entities([battery_sensor, percent_sensor, liter_sensor])

    @callback
    def _async_on_bluetooth_event(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Process incoming BLE Advertisements from Bluetooth Proxy."""
        mfg_data = service_info.manufacturer_data.get(COMPANY_ID)
        if not mfg_data or len(mfg_data) < 3:
            return

        battery = mfg_data[1]
        raw_level = mfg_data[2]

        if battery <= 100 and raw_level <= 100:
            # Aktualisiere die 3 Sensoren
            battery_sensor.update_value(battery)
            percent_sensor.update_value(raw_level)
            liter_sensor.update_value(raw_level)

    bluetooth.async_register_callback(
        hass,
        _async_on_bluetooth_event,
        BluetoothCallbackMatcher(address=mac_address),
        bluetooth.BluetoothScanningMode.PASSIVE,
    )


class GasBaseSensor(SensorEntity):
    """Base class for ble_gastank sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, mac_address: str, key: str, name: str) -> None:
        """Initialize the sensor."""
        self._mac = mac_address
        self._attr_unique_id = f"{mac_address.lower()}_{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_address)},
            name="DIMES Gastank",
            manufacturer="Rotarex",
            model="SRG WAVE",
        )


class GasBatterySensor(GasBaseSensor):
    """1. Sensor: Batterie in %."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:battery"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, mac_address: str) -> None:
        """Initialize battery sensor."""
        super().__init__(mac_address, "battery", "Batterie")

    @callback
    def update_value(self, val: int) -> None:
        """Update entity state."""
        self._attr_native_value = val
        self.async_write_ha_state()


class GasPercentSensor(GasBaseSensor):
    """2. Sensor: Korrigierter Füllstand in % (unter Berücksichtigung des Füllstopps)."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:gauge"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, mac_address: str, fill_stop: float) -> None:
        """Initialize percent sensor."""
        super().__init__(mac_address, "level_percent", "Füllstand")
        self._fill_stop = fill_stop

    @callback
    def update_value(self, raw_level: int) -> None:
        """Berechnet die echten Prozent bezogen auf den Füllstopp."""
        # Da 100% Sensor-Rohwert = Füllstopp entspricht (z. B. 80%),
        # skaliert dieser Sensor den Wert sauber auf die echten 0-100% der Flasche um.
        calc_percent = (float(raw_level) * (self._fill_stop / 100.0))
        self._attr_native_value = round(calc_percent, 1)
        self.async_write_ha_state()


class GasLiterSensor(GasBaseSensor):
    """3. Sensor: Füllstand in Liter."""

    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_icon = "mdi:gas-cylinder"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, mac_address: str, capacity: float, fill_stop: float) -> None:
        """Initialize liter sensor."""
        super().__init__(mac_address, "level_liters", "Füllstand Liter")
        self._capacity = capacity
        self._fill_stop = fill_stop

    @callback
    def update_value(self, raw_level: int) -> None:
        """Berechnet den Inhalt direkt in Litern."""
        # Beispiel 22L Flasche mit 80% Füllstopp -> Max 17.6 L bei 100% Rohwert
        max_usable_liters = self._capacity * (self._fill_stop / 100.0)
        calculated_liters = (float(raw_level) * max_usable_liters) / 100.0
        self._attr_native_value = round(calculated_liters, 1)
        self.async_write_ha_state()
