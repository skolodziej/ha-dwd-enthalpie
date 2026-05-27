"""DataUpdateCoordinator for the DWD Enthalpie integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SOURCE_URL, UPDATE_INTERVAL_MINUTES
from .parser import StationForecast, parse_page

_LOGGER = logging.getLogger(__name__)


class DwdEnthalpieCoordinator(DataUpdateCoordinator[dict[str, StationForecast]]):
    """Fetches the DWD page once and serves all configured stations."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict[str, StationForecast]:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(SOURCE_URL, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching DWD page: {err}") from err

        # Parsing is CPU-bound (small page, ~50KB). Run it in the executor to
        # keep the event loop responsive even on small devices.
        return await self.hass.async_add_executor_job(parse_page, html)
