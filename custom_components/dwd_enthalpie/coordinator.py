"""DataUpdateCoordinator for the DWD Enthalpie integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MAP_BASE_URL, MAP_FILENAMES, SOURCE_URL, UPDATE_INTERVAL_MINUTES
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
        self.last_fetch: datetime | None = None
        # Cached PNG bytes for the 5 Germany-wide forecast maps (index = day offset).
        # None until first successful fetch; stale bytes kept on subsequent failures.
        self.map_images: list[bytes | None] = [None] * len(MAP_FILENAMES)

    async def _async_update_data(self) -> dict[str, StationForecast]:
        session = async_get_clientsession(self.hass)

        # Fetch station HTML and all 5 map images in parallel.
        html_task = asyncio.create_task(self._fetch_html(session))
        maps_task = asyncio.create_task(self._fetch_maps(session))

        try:
            html = await html_task
        except aiohttp.ClientError as err:
            maps_task.cancel()
            raise UpdateFailed(f"Error fetching DWD page: {err}") from err

        # Map fetch failures are non-critical — log warnings inside _fetch_maps.
        await maps_task

        # Parsing is CPU-bound (~50 KB page). Run it in the executor to keep
        # the event loop responsive even on small devices.
        result = await self.hass.async_add_executor_job(parse_page, html)
        self.last_fetch = datetime.now(timezone.utc)
        return result

    async def _fetch_html(self, session: aiohttp.ClientSession) -> str:
        async with session.get(
            SOURCE_URL, timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def _fetch_maps(self, session: aiohttp.ClientSession) -> None:
        """Fetch all 5 forecast map PNGs in parallel (non-critical)."""

        async def _fetch_one(index: int, filename: str) -> None:
            url = MAP_BASE_URL + filename
            try:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    resp.raise_for_status()
                    self.map_images[index] = await resp.read()
            except aiohttp.ClientError as err:
                _LOGGER.warning("Failed to fetch DWD map %s: %s", filename, err)

        await asyncio.gather(*[
            _fetch_one(i, f) for i, f in enumerate(MAP_FILENAMES)
        ])
