"""Config flow and Options flow for BLE Gastank integration."""

from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector

DOMAIN = "ble_gastank"


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
            # Aktualisiert die Daten im Config Entry
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            # Lädt die Integration neu, damit neue Werte sofort greifen
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        current_capacity = self.config_entry.data.get("tank_capacity", 22.0)
        current_fill_stop = self.config_entry.data.get("fill_stop_percent", 80)

        data_schema = vol.Schema(
            {
                vol.Required("tank_capacity", default=current_capacity): vol.Coerce(float),
                vol.Required("fill_stop_percent", default=current_fill_stop): selector.NumberSelector(
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
