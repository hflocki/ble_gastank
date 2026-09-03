"""Config flow and Options flow for BLE Gastank integration."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_SENSOR_TYPE,
    DOMAIN,
    SENSOR_TYPE_DIMES,
    SENSOR_TYPE_TRUMA,
    SENSOR_TYPES,
)


class GasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BLE Gastank."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow properties."""
        self._sensor_type: str | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return GasOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Select Sensor Type."""
        if user_input is not None:
            self._sensor_type = user_input[CONF_SENSOR_TYPE]
            if self._sensor_type == SENSOR_TYPE_TRUMA:
                return await self.async_step_truma()
            return await self.async_step_dimes()

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SENSOR_TYPE, default=SENSOR_TYPE_DIMES
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"label": label, "value": val}
                            for val, label in SENSOR_TYPES.items()
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    async def async_step_dimes(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2a: Configure DIMES Sensor."""
        if user_input is not None:
            formatted_mac = user_input["mac_address"].upper().strip()
            await self.async_set_unique_id(formatted_mac.lower())
            self._abort_if_unique_id_configured()

            user_input["mac_address"] = formatted_mac
            user_input[CONF_SENSOR_TYPE] = SENSOR_TYPE_DIMES

            return self.async_create_entry(
                title=f"DIMES Gastank ({formatted_mac})",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("mac_address"): cv.string,
                vol.Required("tank_capacity", default=22.0): vol.Coerce(float),
                vol.Required("fill_stop_percent", default=80): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=100, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }
        )

        return self.async_show_form(step_id="dimes", data_schema=data_schema)

    async def async_step_truma(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2b: Configure Truma LevelControl Sensor."""
        if user_input is not None:
            formatted_mac = user_input["mac_address"].upper().strip()
            await self.async_set_unique_id(formatted_mac.lower())
            self._abort_if_unique_id_configured()

            user_input["mac_address"] = formatted_mac
            user_input[CONF_SENSOR_TYPE] = SENSOR_TYPE_TRUMA
            # Bei Truma gibt es keinen Füllstopp %, daher setzen wir intern 100%
            user_input["fill_stop_percent"] = 100.0

            return self.async_create_entry(
                title=f"Truma LevelControl ({formatted_mac})",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("mac_address"): cv.string,
                vol.Required("tank_capacity", default=11.0): vol.Coerce(
                    float
                ),  # Hier als kg z.B. 11kg / 5kg
            }
        )

        return self.async_show_form(step_id="truma", data_schema=data_schema)


class GasOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for BLE Gastank."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        sensor_type = self.config_entry.data.get(CONF_SENSOR_TYPE, SENSOR_TYPE_DIMES)
        current_capacity = self.config_entry.data.get(
            "tank_capacity", 22.0 if sensor_type == SENSOR_TYPE_DIMES else 11.0
        )

        schema_dict = {
            vol.Required("tank_capacity", default=current_capacity): vol.Coerce(float),
        }

        if sensor_type == SENSOR_TYPE_DIMES:
            current_fill_stop = self.config_entry.data.get("fill_stop_percent", 80)
            schema_dict[
                vol.Required("fill_stop_percent", default=current_fill_stop)
            ] = selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1, max=100, mode=selector.NumberSelectorMode.BOX
                )
            )

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_dict))
