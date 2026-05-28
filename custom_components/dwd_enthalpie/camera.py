"""Camera platform for DWD Enthalpie — animated forecast loop.

Exposes a single camera entity that cycles through the 5 Germany-wide
enthalpy forecast maps (today + 4 days) at ~0.75 s/frame.

In the Lovelace Camera card, opening the live stream shows the animation.
The card thumbnail shows whichever frame happened to be current when HA
last polled the snapshot.
"""
from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAP_FILENAMES
from .coordinator import DwdEnthalpieCoordinator

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Daten: Deutscher Wetterdienst (DWD), wettergefahren.de"

# Seconds each map is displayed before the next one appears.
FRAME_DURATION: float = 0.75

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
    """Create the animation camera — only once per coordinator lifetime."""
    domain_data: dict[str, Any] = hass.data[DOMAIN]
    coordinator: DwdEnthalpieCoordinator = domain_data[entry.entry_id]

    if "camera_entry" in domain_data:
        return

    domain_data["camera_entry"] = entry.entry_id
    async_add_entities([EnthalpieAnimationCamera(coordinator)])


class EnthalpieAnimationCamera(Camera):
    """Cycles through the 5 DWD enthalpy maps as an MJPEG stream.

    Frame selection is based on wall-clock time so all viewers of the
    stream see the same frame at the same moment.
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_is_streaming = False
    _attr_name = "Vorhersage-Animation"

    def __init__(self, coordinator: DwdEnthalpieCoordinator) -> None:
        super().__init__()
        self._coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_animation_camera"
        self._attr_device_info = _MAPS_DEVICE

    async def async_added_to_hass(self) -> None:
        """Subscribe to coordinator updates to track availability."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self._coordinator.async_add_listener(self._handle_coordinator_update)
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Available once at least one map has been fetched."""
        return any(b is not None for b in self._coordinator.map_images)

    @property
    def frame_interval(self) -> float:
        """Seconds between MJPEG frames — controls animation speed."""
        return FRAME_DURATION

    async def async_camera_image(
        self,
        max_width: int | None = None,
        max_height: int | None = None,
    ) -> bytes | None:
        """Return the current frame based on wall-clock time."""
        frame_idx = int(time.monotonic() / FRAME_DURATION) % len(MAP_FILENAMES)
        return self._coordinator.map_images[frame_idx]
