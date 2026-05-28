"""Sensor platform for DWD Enthalpie."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_STATIONS, DOMAIN, classify
from .coordinator import DwdEnthalpieCoordinator

ATTRIBUTION = "Daten: Deutscher Wetterdienst (DWD), wettergefahren.de"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for each configured station."""
    coordinator: DwdEnthalpieCoordinator = hass.data[DOMAIN][entry.entry_id]
    stations: list[dict[str, str]] = (
        entry.options.get(CONF_STATIONS) or entry.data.get(CONF_STATIONS, [])
    )

    entities: list[SensorEntity] = []
    for s in stations:
        entities.append(EnthalpieValueSensor(coordinator, s["state"], s["station"]))
        entities.append(EnthalpieClassSensor(coordinator, s["state"], s["station"]))

    async_add_entities(entities)


class _BaseStationSensor(CoordinatorEntity[DwdEnthalpieCoordinator], SensorEntity):
    """Common base: device grouping + attribution."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DwdEnthalpieCoordinator,
        state_name: str,
        station: str,
    ) -> None:
        super().__init__(coordinator)
        self._station = station
        self._state_name = state_name
        # One device per station, shared by both sensors.
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, station)},
            name=f"DWD Enthalpie {station}",
            manufacturer="Deutscher Wetterdienst",
            model="Enthalpie / Hitzestress (Hühner)",
            configuration_url="https://www.wettergefahren.de/warnungen/indizes_landwirtschaft/enthalpie.html",
        )

    @property
    def _station_data(self) -> dict[str, Any] | None:
        data = self.coordinator.data or {}
        return data.get(self._station)

    @property
    def available(self) -> bool:
        return super().available and self._station_data is not None


class EnthalpieValueSensor(_BaseStationSensor):
    """Numeric daily-maximum enthalpy value, with 5-day forecast attribute."""

    _attr_translation_key = "enthalpy"
    _attr_native_unit_of_measurement = "kJ/kg"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        coordinator: DwdEnthalpieCoordinator,
        state_name: str,
        station: str,
    ) -> None:
        super().__init__(coordinator, state_name, station)
        self._attr_unique_id = f"{DOMAIN}_{station}_enthalpy".replace(" ", "_")
        self._attr_name = "Enthalpie"

    @property
    def native_value(self) -> int | None:
        d = self._station_data
        return d["today"] if d else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self._station_data
        attrs: dict[str, Any] = {"station": self._station, "bundesland": self._state_name}
        if d:
            attrs["forecast"] = d["forecast"]
        if self.coordinator.last_fetch is not None:
            attrs["last_fetch"] = self.coordinator.last_fetch.isoformat()
        return attrs


class EnthalpieClassSensor(_BaseStationSensor):
    """Text classification: kein/mild/mäßig/stark/extrem Hitzestress."""

    _attr_translation_key = "heat_stress_class"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [
        "no_heat_stress",
        "mild_heat_stress",
        "moderate_heat_stress",
        "severe_heat_stress",
        "extreme_heat_stress",
    ]

    def __init__(
        self,
        coordinator: DwdEnthalpieCoordinator,
        state_name: str,
        station: str,
    ) -> None:
        super().__init__(coordinator, state_name, station)
        self._attr_unique_id = f"{DOMAIN}_{station}_class".replace(" ", "_")
        self._attr_name = "Hitzestress"

    @property
    def native_value(self) -> str | None:
        d = self._station_data
        if not d or d["today"] is None:
            return None
        return classify(d["today"])

    @property
    def icon(self) -> str:
        d = self._station_data
        v = d["today"] if d else None
        if v is None:
            return "mdi:help-circle-outline"
        if v < 50:
            return "mdi:thermometer-low"
        if v < 58:
            return "mdi:thermometer"
        if v < 67:
            return "mdi:thermometer-alert"
        return "mdi:thermometer-high"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self._station_data
        attrs: dict[str, Any] = {"station": self._station, "bundesland": self._state_name}
        if d and d["forecast"]:
            attrs["forecast_classes"] = [
                {"date": f["date"], "class": classify(f["value"]), "value": f["value"]}
                for f in d["forecast"]
            ]
        return attrs
