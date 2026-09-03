"""Sensor platform for BLE Gastank integration."""

from __future__ import annotations

import logging
from datetime import timedelta
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
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_SENSOR_TYPE, DOMAIN, SENSOR_TYPE_DIMES, SENSOR_TYPE_TRUMA
from .devices.dimes import DimesDevice
from .devices.truma import TrumaDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BLE Gastank sensors from a config entry."""
    mac_address = entry.data["mac_address"]
    sensor_type = entry.data.get(CONF_SENSOR_TYPE, SENSOR_TYPE_DIMES)
    tank_capacity = entry.data.get("tank_capacity", 22.0)
    fill_stop_percent = entry.data.get("fill_stop_percent", 80.0)

    # Erstelle alle Entitäten
    battery_sensor = GasTankBatterySensor(
        mac_address, "battery", "Batterie", sensor_type
    )
    raw_sensor = GasTankRawSensor(
        mac_address, "raw_level", "Füllstand Rohwert", sensor_type
    )
    level_sensor = GasTankLevelSensor(
        mac_address, "level", "Füllstand", fill_stop_percent, sensor_type
    )
    liters_sensor = GasTankLitersSensor(
        mac_address,
        "liters",
        "Füllstand Liter",
        tank_capacity,
        fill_stop_percent,
        sensor_type,
    )

    async_add_entities([battery_sensor, raw_sensor, level_sensor, liters_sensor])

    def _update_all_sensors(battery: float, raw_level: float) -> None:
        """Helper to update state across all 4 entities."""
        battery_sensor.update_state(battery)
        raw_sensor.update_state(raw_level)
        level_sensor.update_state(raw_level)
        liters_sensor.update_state(raw_level)

    # Fall 1: DIMES (Passiver Bluetooth Broadcast)
    if sensor_type == SENSOR_TYPE_DIMES:

        @callback
        def _async_on_bluetooth_event(
            service_info: bluetooth.BluetoothServiceInfoBleak,
            change: bluetooth.BluetoothChange,
        ) -> None:
            data = DimesDevice.parse_advertisement(service_info)
            if data:
                _update_all_sensors(data["battery"], data["raw_level"])

        entry.async_on_unload(
            bluetooth.async_register_callback(
                hass,
                _async_on_bluetooth_event,
                bluetooth.BluetoothCallbackMatcher(address=mac_address.upper()),
                bluetooth.BluetoothScanningMode.PASSIVE,
            )
        )

    # Fall 2: Truma LevelControl (Aktiver GATT-Abruf im Intervall)
    elif sensor_type == SENSOR_TYPE_TRUMA:

        async def _async_poll_truma(_now=None) -> None:
            data = await TrumaDevice.async_fetch_data(mac_address)
            if data:
                _update_all_sensors(data["battery"], data["raw_level"])

        # Erstes Mal beim Start ausführen
        hass.async_create_task(_async_poll_truma())

        # Alle 5 Minuten abfragen
        entry.async_on_unload(
            async_track_time_interval(hass, _async_poll_truma, timedelta(minutes=5))
        )


class BaseGasSensor(SensorEntity):
    """Base class for BLE Gastank sensors."""

    _attr_has_entity_name = False

    def __init__(self, mac_address: str, key: str, name: str, sensor_type: str) -> None:
        """Initialize the sensor."""
        self._mac = mac_address
        self._attr_unique_id = f"{mac_address.lower()}_{key}"
        self._attr_name = name

        model_name = (
            "DIMES BLE Sensor"
            if sensor_type == SENSOR_TYPE_DIMES
            else "Truma LevelControl"
        )
        manufacturer_name = "Rotarex" if sensor_type == SENSOR_TYPE_DIMES else "Truma"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_address)},
            name=f"Gastank BLE ({model_name})",
            manufacturer=manufacturer_name,
            model=model_name,
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

    def __init__(
        self,
        mac_address: str,
        key: str,
        name: str,
        fill_stop_percent: float,
        sensor_type: str,
    ) -> None:
        super().__init__(mac_address, key, name, sensor_type)
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
    # Korrektur: TOTAL anstelle von MEASUREMENT für DeviceClass VOLUME
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self,
        mac_address: str,
        key: str,
        name: str,
        tank_capacity: float,
        fill_stop_percent: float,
        sensor_type: str,
    ) -> None:
        super().__init__(mac_address, key, name, sensor_type)
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
