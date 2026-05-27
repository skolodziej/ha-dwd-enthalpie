"""Config flow for DWD Enthalpie integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import BUNDESLAENDER, CONF_STATIONS, DOMAIN, STATIONS_BY_STATE


class DwdEnthalpieConfigFlow(ConfigFlow, domain=DOMAIN):
    """Walk the user through Bundesland → Station, optionally repeating."""

    VERSION = 1

    def __init__(self) -> None:
        self._selected_state: str | None = None
        self._stations: list[dict[str, str]] = []  # [{"state": ..., "station": ...}, ...]

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Step 1: pick a Bundesland."""
        if user_input is not None:
            self._selected_state = user_input["state"]
            return await self.async_step_pick_station()

        schema = vol.Schema(
            {
                vol.Required("state"): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=s, label=s) for s in BUNDESLAENDER
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_pick_station(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: pick a station inside the chosen Bundesland."""
        assert self._selected_state is not None
        already = {(s["state"], s["station"]) for s in self._stations}
        choices = [
            SelectOptionDict(value=name, label=name)
            for name in STATIONS_BY_STATE.get(self._selected_state, ())
            if (self._selected_state, name) not in already
        ]

        if not choices:
            # All stations in this state already added — go back.
            return await self.async_step_user()

        if user_input is not None:
            self._stations.append(
                {"state": self._selected_state, "station": user_input["station"]}
            )
            if user_input.get("add_another"):
                self._selected_state = None
                return await self.async_step_user()

            # Finalize: one config entry holding all selected stations.
            await self.async_set_unique_id(
                ",".join(sorted(s["station"] for s in self._stations))
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._entry_title(),
                data={CONF_STATIONS: self._stations},
            )

        schema = vol.Schema(
            {
                vol.Required("station"): SelectSelector(
                    SelectSelectorConfig(
                        options=choices,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional("add_another", default=False): bool,
            }
        )
        return self.async_show_form(
            step_id="pick_station",
            data_schema=schema,
            description_placeholders={"state": self._selected_state},
        )

    def _entry_title(self) -> str:
        if len(self._stations) == 1:
            return f"DWD Enthalpie – {self._stations[0]['station']}"
        return f"DWD Enthalpie ({len(self._stations)} Stationen)"

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return DwdEnthalpieOptionsFlow(entry)


class DwdEnthalpieOptionsFlow(OptionsFlow):
    """Add or remove stations after initial setup."""

    def __init__(self, entry: ConfigEntry) -> None:
        # Don't reference self.config_entry directly — that's deprecated in 2024.12+.
        # The platform passes the entry into __init__; store our own reference.
        self._entry = entry
        self._selected_state: str | None = None
        self._stations: list[dict[str, str]] = list(
            entry.options.get(CONF_STATIONS) or entry.data.get(CONF_STATIONS, [])
        )

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Show the menu: add station / remove station / finish."""
        if user_input is not None:
            action = user_input["action"]
            if action == "add":
                return await self.async_step_add_state()
            if action == "remove":
                return await self.async_step_remove()
            return self._finish()

        schema = vol.Schema(
            {
                vol.Required("action", default="add"): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value="add", label="Station hinzufügen"),
                            SelectOptionDict(value="remove", label="Station entfernen"),
                            SelectOptionDict(value="done", label="Fertig"),
                        ],
                        mode=SelectSelectorMode.LIST,
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={
                "current": ", ".join(s["station"] for s in self._stations) or "—"
            },
        )

    async def async_step_add_state(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._selected_state = user_input["state"]
            return await self.async_step_add_station()

        schema = vol.Schema(
            {
                vol.Required("state"): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=s, label=s) for s in BUNDESLAENDER
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="add_state", data_schema=schema)

    async def async_step_add_station(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        assert self._selected_state is not None
        already = {(s["state"], s["station"]) for s in self._stations}
        choices = [
            SelectOptionDict(value=name, label=name)
            for name in STATIONS_BY_STATE.get(self._selected_state, ())
            if (self._selected_state, name) not in already
        ]

        if not choices:
            return await self.async_step_init()

        if user_input is not None:
            self._stations.append(
                {"state": self._selected_state, "station": user_input["station"]}
            )
            return await self.async_step_init()

        schema = vol.Schema(
            {
                vol.Required("station"): SelectSelector(
                    SelectSelectorConfig(
                        options=choices,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="add_station",
            data_schema=schema,
            description_placeholders={"state": self._selected_state},
        )

    async def async_step_remove(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if not self._stations:
            return await self.async_step_init()

        if user_input is not None:
            to_remove = set(user_input.get("stations", []))
            self._stations = [s for s in self._stations if s["station"] not in to_remove]
            return await self.async_step_init()

        schema = vol.Schema(
            {
                vol.Optional("stations", default=[]): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=s["station"], label=s["station"])
                            for s in self._stations
                        ],
                        multiple=True,
                        mode=SelectSelectorMode.LIST,
                    )
                )
            }
        )
        return self.async_show_form(step_id="remove", data_schema=schema)

    def _finish(self) -> ConfigFlowResult:
        return self.async_create_entry(
            title="",
            data={CONF_STATIONS: self._stations},
        )
