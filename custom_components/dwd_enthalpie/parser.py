"""HTML parser for the DWD Enthalpie page.

The page contains one <table> per Bundesland. Each row has the station name in
the first <td> and the five daily forecast values (today + 4 days) in the next
five <td>s.

We use BeautifulSoup with lxml-ish parsing via the stdlib html.parser to avoid
extra dependencies; bs4 is already pulled in by Home Assistant core.
"""
from __future__ import annotations

import logging
from datetime import date
from typing import TypedDict

from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)


class StationForecast(TypedDict):
    """One station's parsed forecast."""

    station: str
    today: int | None
    forecast: list[ForecastDay]


class ForecastDay(TypedDict):
    """A single day in the 5-day forecast."""

    date: str  # ISO date "YYYY-MM-DD"
    value: int | None


def parse_page(html: str) -> dict[str, StationForecast]:
    """Parse the DWD enthalpy HTML page.

    Returns a dict mapping station name -> StationForecast.
    """
    soup = BeautifulSoup(html, "html.parser")
    out: dict[str, StationForecast] = {}

    for table in soup.find_all("table"):
        header_row = table.find("tr")
        if not header_row:
            continue

        # We only care about the daily forecast tables. Those have a first
        # header cell that says "Stationsname".
        first_cell = header_row.find(["th", "td"])
        if not first_cell or "stationsname" not in first_cell.get_text(strip=True).lower():
            continue

        # Parse the 5 date columns from the header row.
        header_cells = header_row.find_all(["th", "td"])
        dates = _extract_dates(header_cells[1:6])

        for row in table.find_all("tr")[1:]:  # skip header
            cells = row.find_all(["td", "th"])
            if len(cells) < 6:
                continue

            name = cells[0].get_text(strip=True)
            # Skip the repeated footer row (same as header)
            if name.lower() == "stationsname":
                continue

            values = [_to_int(c.get_text(strip=True)) for c in cells[1:6]]
            forecast: list[ForecastDay] = [
                {"date": d, "value": v} for d, v in zip(dates, values, strict=False)
            ]
            out[name] = {
                "station": name,
                "today": values[0] if values else None,
                "forecast": forecast,
            }

    _LOGGER.debug("Parsed %d stations from DWD page", len(out))
    return out


def _to_int(text: str) -> int | None:
    """Parse a cell value to int, returning None on '---' or empty cells."""
    text = text.strip()
    if not text or text in {"---", "—", "-"}:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _extract_dates(cells) -> list[str]:
    """Extract ISO dates from header cells like 'Mi (Mittwoch) 27.05.'.

    The year is not in the source, so we guess: take the current year, but if
    the parsed date is more than 60 days in the past, roll forward one year.
    """
    today = date.today()
    out: list[str] = []
    for cell in cells:
        text = cell.get_text(" ", strip=True)
        # Find the dd.mm. token
        dmy: date | None = None
        for token in text.replace("(", " ").replace(")", " ").split():
            token = token.strip(".")
            if "." in token:
                parts = token.split(".")
                if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                    try:
                        d = int(parts[0])
                        m = int(parts[1])
                        candidate = date(today.year, m, d)
                        # If the page shows December dates and we're in January,
                        # they belong to the previous year. Conversely if it
                        # shows January dates and we're in December, next year.
                        if (candidate - today).days < -60:
                            candidate = date(today.year + 1, m, d)
                        elif (candidate - today).days > 300:
                            candidate = date(today.year - 1, m, d)
                        dmy = candidate
                        break
                    except ValueError:
                        continue
        out.append(dmy.isoformat() if dmy else "")
    return out
