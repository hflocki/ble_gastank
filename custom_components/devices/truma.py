"""Truma LevelControl BLE Parser and Handler."""

from __future__ import annotations

import logging

from bleak import BleakClient

from ..const import TRUMA_MEASUREMENT_DATA_UUID

_LOGGER = logging.getLogger(__name__)


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

                raw_bytes = await client.read_gatt_char(TRUMA_MEASUREMENT_DATA_UUID)
                _LOGGER.debug("Raw bytes received from Truma: %s", raw_bytes.hex())

                # Parsing-Logik für Truma Measurement Data Payload
                # Beispielhafter Dummy/Erster Entwurf der Byte-Auswertung:
                if len(raw_bytes) >= 2:
                    battery = float(raw_bytes[0]) if raw_bytes[0] <= 100 else 100.0
                    raw_level = float(raw_bytes[1])
                    return {
                        "battery": battery,
                        "raw_level": raw_level,
                    }

        except Exception as err:
            _LOGGER.error(
                "Error reading Truma LevelControl GATT data (%s): %s", mac_address, err
            )

        return None
