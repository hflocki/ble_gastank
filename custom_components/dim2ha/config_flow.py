"""Config flow for BLE Gastank integration."""

from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector

DOMAIN = "ble_gastank"


class GasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BLE Gastank."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            formatted_mac = user_input["mac_address"].upper().strip()
            
            # Verhindert, dass dieselbe MAC-Adresse doppelt angelegt wird
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
            step_id="user", data_schema=data_schema, errors=errors
        )
