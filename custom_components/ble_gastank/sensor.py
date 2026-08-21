"""Sensor platform for BLE Gastank integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import bluetooth
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

DOMAIN = "ble_gastank"
COMPANY_ID = 0xFFFF  # GGf. auf die korrekte BLE Manufacturer ID anpassen

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BLE Gastank sensors from a config entry."""
    mac_address = entry.data["mac_address"]
    tank_capacity = entry.data.get("tank_capacity", 22.0)
    fill_stop_percent = entry.data.get("fill_stop_percent", 80.0)

    # Erstelle alle 4 Sensoren
    battery_sensor = GasTankBatterySensor(mac_address, "battery", "Batterie")
    raw_sensor = GasTankRawSensor(mac_address, "raw_level", "Füllstand Rohwert")
    level_sensor = GasTankLevelSensor(mac_address, "level", "Füllstand", fill_stop_percent)
    liters_sensor = GasTankLitersSensor(
        mac_address, "liters", "Füllstand Liter", tank_capacity, fill_stop_percent
    )

    async_add_entities([battery_sensor, raw_sensor, level_sensor, liters_sensor])

    @callback
    def _async_on_bluetooth_event(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Handle incoming passive BLE broadcast data."""
        mfg_data = service_info.manufacturer_data.get(COMPANY_ID)
        if not mfg_data or len(mfg_data) < 3:
            return

        battery = mfg_data[1]
        raw_level = mfg_data[2]

        if battery <= 100 and raw_level <= 100:
            battery_sensor.update_state(battery)
            raw_sensor.update_state(raw_level)
            level_sensor.update_state(raw_level)
            liters_sensor.update_state(raw_level)

    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            _async_on_bluetooth_event,
            bluetooth.BluetoothCallbackMatcher(address=mac_address.upper()),
            bluetooth.BluetoothScanningMode.PASSIVE,
        )
    )


class BaseGasSensor(SensorEntity):
    """Base class for BLE Gastank sensors."""

    _attr_has_entity_name = False

    def __init__(self, mac_address: str, key: str, name: str) -> None:
        """Initialize the sensor."""
        self._mac = mac_address
        self._attr_unique_id = f"{mac_address.lower()}_{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_address)},
            name="Gastank BLE",
            manufacturer="Generic BLE",
            model="BLE Gas Sensor",
        )

    def update_state(self, value: float) -> None:
        """Update sensor state."""
        self._attr_native_value = value
        self.async_write_ha_state()


class GasTankBatterySensor(BaseGasSensor):
    """Sensor for BLE battery level."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT


class GasTankRawSensor(BaseGasSensor):
    """Sensor for uncalibrated raw sensor level."""

    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT


class GasTankLevelSensor(BaseGasSensor):
    """Sensor for fill percentage scaled to effective stop."""

    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, mac_address: str, key: str, name: str, fill_stop_percent: float) -> None:
        super().__init__(mac_address, key, name)
        self._fill_stop_percent = fill_stop_percent

    def update_state(self, raw_level: float) -> None:
        """Calculate percentage scaled to the configured fill stop."""
        if self._fill_stop_percent > 0:
            scaled_percent = min(100.0, (raw_level / self._fill_stop_percent) * 100.0)
        else:
            scaled_percent = raw_level
        self._attr_native_value = round(scaled_percent, 1)
        self.async_write_ha_state()


class GasTankLitersSensor(BaseGasSensor):
    """Sensor for remaining gas in liters."""

    _attr_device_class = SensorDeviceClass.VOLUME
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, mac_address: str, key: str, name: str, tank_capacity: float, fill_stop_percent: float
    ) -> None:
        super().__init__(mac_address, key, name)
        self._usable_capacity = tank_capacity * (fill_stop_percent / 100.0)
        self._fill_stop_percent = fill_stop_percent

    def update_state(self, raw_level: float) -> None:
        """Calculate remaining volume in liters based on raw sensor value."""
        if self._fill_stop_percent > 0:
            liters = (raw_level / self._fill_stop_percent) * self._usable_capacity
            liters = min(self._usable_capacity, liters)
        else:
            liters = 0.0
        self._attr_native_value = round(liters, 1)
        self.async_write_ha_state()
