"""DIMES BLE Sensor Parser."""

from __future__ import annotations

import logging

from ..const import COMPANY_ID_DIMES

_LOGGER = logging.getLogger(__name__)


class DimesDevice:
    """Handling and parsing for DIMES BLE Gas Sensor."""

    @staticmethod
    def parse_advertisement(service_info) -> dict[str, float] | None:
        """Parse incoming passive BLE broadcast data for DIMES."""
        mfg_data = service_info.manufacturer_data.get(COMPANY_ID_DIMES)
        if not mfg_data or len(mfg_data) < 3:
            return None

        battery = mfg_data[1]
        raw_level = mfg_data[2]

        if battery <= 100 and raw_level <= 100:
            return {
                "battery": float(battery),
                "raw_level": float(raw_level),
            }

        return None
