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
    SENSOR_TYPES,
)


class GasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BLE Gastank."""

    VERSION = 1

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
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            formatted_mac = user_input["mac_address"].upper().strip()

            await self.async_set_unique_id(formatted_mac.lower())
            self._abort_if_unique_id_configured()

            user_input["mac_address"] = formatted_mac

            return self.async_create_entry(
                title=f"BLE Gastank ({formatted_mac})",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("mac_address"): cv.string,
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
                vol.Required("tank_capacity", default=22.0): vol.Coerce(float),
                vol.Required("fill_stop_percent", default=80): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=100,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "fill_stop_note": "Hinweis: Wenn kein mechanischer Füllstopp vorhanden ist, trage bitte 100% ein."
            },
        )


class GasOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for BLE Gastank (Nachträgliches Ändern)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        current_capacity = self.config_entry.data.get("tank_capacity", 22.0)
        current_fill_stop = self.config_entry.data.get("fill_stop_percent", 80)
        current_sensor_type = self.config_entry.data.get(
            CONF_SENSOR_TYPE, SENSOR_TYPE_DIMES
        )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SENSOR_TYPE, default=current_sensor_type
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"label": label, "value": val}
                            for val, label in SENSOR_TYPES.items()
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required("tank_capacity", default=current_capacity): vol.Coerce(
                    float
                ),
                vol.Required(
                    "fill_stop_percent", default=current_fill_stop
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=100,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
