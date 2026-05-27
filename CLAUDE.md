# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Home Assistant custom integration (HACS-compatible) that fetches the DWD (Deutscher Wetterdienst) enthalpy / heat-stress index for cattle farming. It scrapes one HTML page, parses ~600 German weather stations, and exposes two sensors per configured station: a numeric kJ/kg value and a text heat-stress class.

## Validation / CI

There is no local test suite. The CI runs two validators via GitHub Actions:

- **HACS validation** — checks manifest/hacs.json structure and repository layout
- **Hassfest** — Home Assistant's own integration validator (checks manifest, config flow, etc.)

To validate locally, you need a Home Assistant dev environment. The fastest path is the [Home Assistant development container](https://developers.home-assistant.io/docs/development_environment).

```bash
# Inside a HA dev environment:
python -m script.hassfest
```

The only runtime dependency beyond Home Assistant's built-ins is `beautifulsoup4>=4.12.0` (declared in `manifest.json`).

## Architecture

All code lives in `custom_components/dwd_enthalpie/`:

- **`__init__.py`** — entry setup/teardown. A single shared `DwdEnthalpieCoordinator` is created for the first config entry and reused by all subsequent entries, so only one HTTP request is made regardless of how many stations are configured.
- **`coordinator.py`** — `DataUpdateCoordinator` subclass. Fetches the DWD HTML page every 60 minutes via `aiohttp`, then runs `parse_page()` in the executor (CPU-bound scraping off the event loop).
- **`parser.py`** — BeautifulSoup parser. Iterates `<table>` elements, identifies station forecast tables by a "Stationsname" header cell, and returns `dict[station_name → StationForecast]`. Handles the missing year in DWD date columns (`dd.mm.` format).
- **`sensor.py`** — Two sensor classes per station, both inheriting `_BaseStationSensor`. `EnthalpieValueSensor` exposes the numeric value + `forecast` attribute; `EnthalpieClassSensor` exposes the enum class + `forecast_classes` attribute.
- **`config_flow.py`** — Two-step UI flow (Bundesland → Station) with an "add another" checkbox. `DwdEnthalpieOptionsFlow` allows adding/removing stations after setup.
- **`const.py`** — All constants, the `classify()` function, and the complete static station list (`STATIONS_BY_STATE`). **Update this file when the DWD changes its station list.**
- **`strings.json`** / **`translations/en.json`** / **`translations/de.json`** — UI strings for config flow steps and entity names/states. Required by hassfest. `strings.json` and `en.json` are identical (HA convention).

## Key design decisions

- One coordinator for all config entries — the DWD page contains every station; fetching it multiple times would be wasteful.
- Station list is static in `const.py` rather than scraped dynamically during config flow, to avoid a network dependency at setup time.
- `OptionsFlow.__init__` stores `entry` as `self._entry` rather than using `self.config_entry` (deprecated in HA 2024.12+).
- `unique_id` for a config entry is a sorted, comma-joined list of station names — changing the station set requires a new entry.
