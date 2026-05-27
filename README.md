# DWD Enthalpie (Hitzestress) für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/docs/faq/custom_repositories)

Home Assistant Custom Integration für den **Enthalpie-Index (Hitzestress für Rinder)**
des Deutschen Wetterdienstes (DWD).

Quelle: <https://www.wettergefahren.de/warnungen/indizes_landwirtschaft/enthalpie.html>

## Was ist Enthalpie / Hitzestress?

Der DWD veröffentlicht für rund 600 deutsche Wetterstationen täglich das prognostizierte
**Tagesmaximum der Enthalpie** (in kJ/kg) für heute + 4 Folgetage. Aus diesem Wert
leitet der DWD eine Hitzestress-Klasse ab — relevant vor allem für die Rinderhaltung:

| Enthalpie (kJ/kg) | Klasse                  |
| ----------------- | ----------------------- |
| < 50              | kein Hitzestress        |
| 50 – < 58         | milder Hitzestress      |
| 58 – < 67         | mäßiger Hitzestress     |
| 67 – < 72         | starker Hitzestress     |
| ≥ 72              | extremer Hitzestress    |

## Funktionsumfang

- 📍 **Stationsauswahl per UI** — erst Bundesland, dann Station aus Dropdown
- 🏠 **Mehrere Stationen** pro Installation (z. B. Heimatort + Stallstandort)
- 📊 **Pro Station zwei Sensoren**:
  - `sensor.dwd_enthalpie_<station>_enthalpie` — numerischer Wert in kJ/kg
  - `sensor.dwd_enthalpie_<station>_hitzestress` — Klasse als Text (`enum`-Sensor)
- 🗓️ **5-Tage-Forecast** als Attribut (`forecast`, `forecast_classes`)
- 🌐 **Mehrsprachig** — Deutsch und Englisch
- 🔁 **Ein HTTP-Request für alle Stationen** — schont den DWD-Server
- 🔄 **Optionen-Flow** — Stationen nachträglich hinzufügen / entfernen

## Installation

### Via HACS (empfohlen)

1. HACS → Integrationen → Drei-Punkte-Menü → „Custom repositories"
2. URL dieses Repos eintragen, Kategorie „Integration"
3. „DWD Enthalpie (Hitzestress)" installieren
4. Home Assistant neu starten
5. Einstellungen → Geräte & Dienste → „Integration hinzufügen" → „DWD Enthalpie"

### Manuell

1. Den Ordner `custom_components/dwd_enthalpie/` in dein Home-Assistant-`config/`-
   Verzeichnis kopieren (Endstruktur: `config/custom_components/dwd_enthalpie/…`)
2. Home Assistant neu starten
3. Integration über die UI hinzufügen

## Konfiguration

Komplett über die UI. Beim Hinzufügen:

1. **Bundesland wählen** (16 Optionen)
2. **Station wählen** aus dem Dropdown der Stationen in diesem Bundesland
3. Optional Häkchen „Weitere Station hinzufügen" → zurück zu Schritt 1
4. Fertig — pro Station erscheint ein Gerät mit zwei Entitäten

Nachträgliche Änderungen über „Konfigurieren" auf der Integrationskachel.

## Beispiel-Automation

```yaml
automation:
  - alias: "Stallventilation bei Hitzestress"
    trigger:
      - platform: state
        entity_id: sensor.dwd_enthalpie_rotenburg_wumme_hitzestress
        to:
          - "severe_heat_stress"
          - "extreme_heat_stress"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.stallventilator
      - service: notify.mobile_app_handy
        data:
          title: "Hitzestress-Warnung"
          message: >
            {{ states('sensor.dwd_enthalpie_rotenburg_wumme_enthalpie') }} kJ/kg
            in Rotenburg/Wümme – Stallventilation aktiviert.
```

## Lovelace-Beispiel

Die 5-Tage-Vorhersage ist als Attribut verfügbar und lässt sich mit dem
[apexcharts-card](https://github.com/RomRider/apexcharts-card) o. ä. visualisieren:

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Enthalpie-Vorhersage Rotenburg
series:
  - entity: sensor.dwd_enthalpie_rotenburg_wumme_enthalpie
    data_generator: |
      return entity.attributes.forecast.map((f) => [
        new Date(f.date).getTime(), f.value
      ]);
```

## Datenquelle & Lizenz

- **Daten**: Deutscher Wetterdienst (DWD), CC BY 4.0 — Attribution erfolgt automatisch
  über das `attribution`-Feld jedes Sensors.
- **Code**: MIT License — siehe [LICENSE](LICENSE).

## Disclaimer

Diese Integration ist ein inoffizielles Hobbyprojekt und steht in keinem Zusammenhang
mit dem Deutschen Wetterdienst. Die Werte werden 1× pro Stunde abgerufen — der DWD
aktualisiert die Prognose typischerweise einmal täglich.

## Beitragen

PRs willkommen — insbesondere wenn der DWD die Stationsliste ändert.
Die Stations-Tabelle steht in [`const.py`](custom_components/dwd_enthalpie/const.py).

## Verwandte Indizes

Der DWD veröffentlicht weitere landwirtschaftliche Warnindizes
([Bodenfrost](https://www.wettergefahren.de/warnungen/indizes_landwirtschaft/bodenfrost.html),
[Clomazone](https://www.wettergefahren.de/warnungen/indizes_landwirtschaft/clomazone.html)).
Diese könnten in einer späteren Version ergänzt werden — Issues / PRs willkommen.
