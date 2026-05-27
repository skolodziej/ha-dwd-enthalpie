"""DWD Enthalpie (Hitzestress) integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import DwdEnthalpieCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DWD Enthalpie from a config entry."""
    # Reuse a single coordinator across all config entries — the DWD page
    # contains every station, so one HTTP request serves everyone.
    coordinator: DwdEnthalpieCoordinator | None = hass.data.get(DOMAIN, {}).get("coordinator")
    if coordinator is None:
        coordinator = DwdEnthalpieCoordinator(hass)
        await coordinator.async_config_entry_first_refresh()
        hass.data.setdefault(DOMAIN, {})["coordinator"] = coordinator

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change (e.g. station added/removed)."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        # If no entries left, drop the coordinator too.
        if not any(k for k in hass.data[DOMAIN] if k != "coordinator"):
            hass.data[DOMAIN].pop("coordinator", None)
    return unloaded
