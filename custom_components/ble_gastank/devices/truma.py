"""Truma LevelControl BLE Parser and Handler."""

from __future__ import annotations

import logging
import struct

from bleak import BleakClient

from ..const import TRUMA_MEASUREMENT_DATA_UUID

_LOGGER = logging.getLogger(__name__)

BATTERY_CHAR_UUID = "00002a19-0000-1000-8000-00805f9b34fb"


class TrumaDevice:
    """Handling and GATT communication for Truma LevelControl."""

    @staticmethod
    async def async_fetch_data(mac_address: str) -> dict[str, float] | None:
        """Connect via GATT and read measurement data from Truma LevelControl."""
        try:
            async with BleakClient(mac_address, timeout=10.0) as client:
                if not client.is_connected:
                    _LOGGER.warning(
                        "Could not connect to Truma LevelControl at %s", mac_address
                    )
                    return None

                # 1. Batterie auslesen (Standard BLE Battery Characteristic)
                battery = 100.0
                try:
                    bat_bytes = await client.read_gatt_char(BATTERY_CHAR_UUID)
                    if bat_bytes:
                        battery = float(bat_bytes[0])
                except Exception as bat_err:
                    _LOGGER.debug("Could not read battery level: %s", bat_err)

                # 2. Messdaten auslesen
                raw_bytes = await client.read_gatt_char(TRUMA_MEASUREMENT_DATA_UUID)
                _LOGGER.debug("Raw bytes received from Truma: %s", raw_bytes.hex())

                if len(raw_bytes) < 8:
                    _LOGGER.warning("Truma payload too short: %d bytes", len(raw_bytes))
                    return None

                # Raw1: Byte 2 & 3 (Little Endian uint16_t)
                raw1 = struct.unpack_from("<H", raw_bytes, 2)[0]
                # Raw2: Byte 6 & 7 (Little Endian uint16_t)
                raw2 = struct.unpack_from("<H", raw_bytes, 6)[0]

                # Prozentberechnung gemäß Formel
                if raw1 == 0 or raw2 == 0:
                    raw_level = 0.0
                else:
                    pct = ((float(raw1) - 46.5) / (364.0 - 46.5)) * 100.0
                    raw_level = max(0.0, min(100.0, pct))

                return {
                    "battery": battery,
                    "raw_level": raw_level,
                }

        except Exception as err:
            _LOGGER.error(
                "Error reading Truma LevelControl GATT data (%s): %s", mac_address, err
            )

        return None
