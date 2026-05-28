"""Image platform for DWD Enthalpie forecast maps.

Five Germany-wide PNG maps are published by DWD for today + 4 forecast days.
They are not per-station, so we create them exactly once (tied to whichever
config entry first sets up the shared coordinator).
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp
from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAP_BASE_URL
from .coordinator import DwdEnthalpieCoordinator

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Daten: Deutscher Wetterdienst (DWD), wettergefahren.de"

# (unique key suffix, entity display name, filename)
_MAPS: list[tuple[str, str, str]] = [
    ("map_today", "heute",        "enth_stationen.png"),
    ("map_day1",  "morgen",       "enth_stationen1.png"),
    ("map_day2",  "übermorgen",   "enth_stationen2.png"),
    ("map_day3",  "3. Folgetag",  "enth_stationen3.png"),
    ("map_day4",  "4. Folgetag",  "enth_stationen4.png"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the 5 map image entities — only once per coordinator lifetime."""
    domain_data: dict[str, Any] = hass.data[DOMAIN]
    coordinator: DwdEnthalpieCoordinator = domain_data[entry.entry_id]

    # Maps are Germany-wide; only create them for the first entry that runs.
    # When that entry is removed, __init__.async_unload_entry clears maps_entry
    # so the next HA restart (or reload) will re-create them.
    if "maps_entry" in domain_data:
        return

    domain_data["maps_entry"] = entry.entry_id
    async_add_entities([
        EnthalpieMapImage(coordinator, key, name, MAP_BASE_URL + filename)
        for key, name, filename in _MAPS
    ])


class EnthalpieMapImage(ImageEntity):
    """One DWD enthalpy forecast map (PNG, updated ~daily by DWD)."""

    _attr_attribution = ATTRIBUTION
    _attr_content_type = "image/png"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DwdEnthalpieCoordinator,
        key: str,
        name: str,
        url: str,
    ) -> None:
        ImageEntity.__init__(self, coordinator.hass)
        self._coordinator = coordinator
        self._key = key
        self._url = url
        # Per-fetch image cache: avoids re-downloading the same PNG for
        # multiple Lovelace clients hitting the HA image proxy concurrently.
        self._cached_bytes: bytes | None = None
        self._cached_for: datetime | None = None
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "maps")},
            name="DWD Enthalpie Karten",
            manufacturer="Deutscher Wetterdienst",
            model="Enthalpie / Hitzestress (Rinder)",
            configuration_url="https://www.wettergefahren.de/warnungen/indizes_landwirtschaft/enthalpie.html",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to coordinator so image_last_updated refreshes each hour."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self._handle_coordinator_update)
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Write state when coordinator fetches new data (updates image_last_updated)."""
        self.async_write_ha_state()

    @property
    def image_last_updated(self) -> datetime | None:
        """Return the coordinator's last successful fetch time.

        HA uses this as the entity state and as a cache-buster in the image
        proxy URL, so the browser refetches the map after each hourly refresh.
        """
        return self._coordinator.last_fetch

    async def async_image(self) -> bytes | None:
        """Return PNG bytes, re-fetching from DWD only when the coordinator refreshed."""
        current_fetch = self._coordinator.last_fetch

        # Return cached bytes if they are still current.
        if self._cached_bytes is not None and self._cached_for == current_fetch:
            return self._cached_bytes

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                self._url, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                resp.raise_for_status()
                self._cached_bytes = await resp.read()
                self._cached_for = current_fetch
        except aiohttp.ClientError as err:
            _LOGGER.warning("Failed to fetch DWD enthalpy map %s: %s", self._key, err)

        # On failure, return stale bytes if available rather than None.
        return self._cached_bytes
