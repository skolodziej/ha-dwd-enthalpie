"""Image platform for DWD Enthalpie forecast maps.

Five Germany-wide PNG maps are published by DWD for today + 4 forecast days.
The coordinator fetches them in parallel with the station data; this platform
simply exposes them as image entities.

Maps are not per-station, so they are created exactly once (tied to whichever
config entry first sets up the shared coordinator).
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAP_FILENAMES
from .coordinator import DwdEnthalpieCoordinator

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Daten: Deutscher Wetterdienst (DWD), wettergefahren.de"

# (unique key suffix, entity display name) — index matches MAP_FILENAMES / coordinator.map_images
_MAP_META: list[tuple[str, str]] = [
    ("map_today", "heute"),
    ("map_day1",  "morgen"),
    ("map_day2",  "übermorgen"),
    ("map_day3",  "3. Folgetag"),
    ("map_day4",  "4. Folgetag"),
]

_MAPS_DEVICE = DeviceInfo(
    identifiers={(DOMAIN, "maps")},
    name="DWD Enthalpie Karten",
    manufacturer="Deutscher Wetterdienst",
    model="Enthalpie / Hitzestress (Rinder)",
    configuration_url="https://www.wettergefahren.de/warnungen/indizes_landwirtschaft/enthalpie.html",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the 5 map image entities — only once per coordinator lifetime."""
    domain_data: dict[str, Any] = hass.data[DOMAIN]
    coordinator: DwdEnthalpieCoordinator = domain_data[entry.entry_id]

    if "maps_entry" in domain_data:
        return

    domain_data["maps_entry"] = entry.entry_id
    async_add_entities([
        EnthalpieMapImage(coordinator, index, key, name)
        for index, (key, name) in enumerate(_MAP_META)
    ])


class EnthalpieMapImage(ImageEntity):
    """One DWD enthalpy forecast map (PNG, updated ~daily by DWD)."""

    _attr_attribution = ATTRIBUTION
    _attr_content_type = "image/png"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DwdEnthalpieCoordinator,
        index: int,
        key: str,
        name: str,
    ) -> None:
        ImageEntity.__init__(self, coordinator.hass)
        self._coordinator = coordinator
        self._index = index
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_name = name
        self._attr_device_info = _MAPS_DEVICE

    async def async_added_to_hass(self) -> None:
        """Subscribe to coordinator so image_last_updated refreshes each hour."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self._handle_coordinator_update)
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def image_last_updated(self) -> datetime | None:
        """Coordinator's last successful fetch time — used as image cache-buster."""
        return self._coordinator.last_fetch

    async def async_image(self) -> bytes | None:
        """Return the pre-fetched PNG bytes from the coordinator's cache."""
        return self._coordinator.map_images[self._index]
