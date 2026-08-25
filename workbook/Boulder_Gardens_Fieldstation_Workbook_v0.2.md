---
title: Boulder Gardens Fieldstation Workbook
version: 0.2
started: 2026-07-31
status: living-source-record
rule: Field reports are derived from this workbook.
---

# Boulder Gardens Fieldstation Workbook

**Purpose:** Permanent working record for observations, equipment details, photographs,
instrument readings, calculations, uncertainties, corrections, and later changes.

## Record status

- **CONFIRMED** — visible in a source image, instrument reading, equipment label, or primary record.
- **RECORDED** — supplied by Robert and retained as part of the project record.
- **CALCULATED** — derived directly from confirmed or recorded numbers.
- **TO VERIFY** — needs a photograph, label, measurement, or correction.

## Workbook index

| Record | Subject | Status | Date |
|---|---|---|---|
| FR001 | Command Center solar system | Source record opened | 2026-07-31 |

# FR001 — Command Center Solar System

- **Record status:** Open
- **Observation date:** 2026-07-31
- **Instrument time:** 4:10 PM
- **Location:** Command Center
- **Observer:** Robert Redecker
- **Subjects:** Solar, battery, infrastructure
- **Public report:** Not yet published

## Scope

This record begins with the working photovoltaic and battery system serving the
Command Center. PoE, Meshtastic, remote sensors, Home Assistant, and related
infrastructure will be linked later as separate observations.

## Core observations

- **RECORDED:** Present working array: 6 × 295 W photovoltaic modules.
- **CALCULATED:** Present array nameplate capacity: 1,770 W / 1.77 kW.
- **RECORDED:** Battery bank: 16 LiFePO4 cells in series.
- **RECORDED:** Cell rating: 3.2 V, 280 Ah.
- **CALCULATED:** Nominal pack voltage: 51.2 V.
- **CALCULATED:** Nominal stored energy: 14,336 Wh / approximately 14.3 kWh.
- **RECORDED:** Inverter: Schneider XW Pro 6848.
- **TO VERIFY:** OutBack charge-controller exact model.
- **CONFIRMED:** JK-BMS configured capacity displayed as 270.0 Ah.

## Instrument observation — JK-BMS

Source: `sources/FR001_JK-BMS_2026-07-31_1610.jpg`

| Observed field | Reading |
|---|---:|
| State of charge | 79% |
| Pack voltage | 53.48 V |
| Current | -1.73 A |
| Power | 92.5 W |
| Operating state | Discharging |
| Estimated time remaining | 123 h 26 min 33 sec |
| Configured capacity | 270.0 Ah |
| Remaining capacity | 213.4 Ah |
| Highest cell | 3.344 V |
| Lowest cell | 3.342 V |
| Displayed voltage difference | 0.004 V |
| Balancing current | 0.000 A |
| Highest reported temperature | 39.0 °C |
| Cell type | LFP |
| Charge control | ON |
| Discharge control | ON |
| Balancing | OFF |

**Preservation note:** The application displayed a 0.004 V pack spread while
the displayed high and low values differ by 0.002 V. Both are retained exactly
as shown.

## Calculated values

| Quantity | Inputs | Result |
|---|---|---:|
| Present PV nameplate | 6 × 295 W | 1,770 W / 1.77 kW |
| Nominal battery voltage | 16 × 3.2 V | 51.2 V |
| Nominal battery energy | 51.2 V × 280 Ah | 14.3 kWh |
| Configured BMS energy | 51.2 V × 270 Ah | 13.8 kWh |

## Photographic source record

| Source ID | File | Observed content | Date basis |
|---|---|---|---|
| FR001-S01 | `sources/fr001/FR001-S01_JK-BMS_2026-07-31_1610.jpg` | JK-BMS status screen showing the recorded battery reading | Screen time and report date |
| FR001-S02 | `sources/fr001/FR001-S02_Robert-open-inverter_2025-09-01.jpg` | Robert beside the open Schneider inverter while work is underway | Visible photograph timestamp |
| FR001-S03 | `sources/fr001/FR001-S03_wide-setting_2026-01-31_0845.jpg` | Wide view of ground-mounted panels and the surrounding working area | Image metadata |
| FR001-S04 | `sources/fr001/FR001-S04_array-approach_2026-07-25_1722.jpg` | Ground-mounted modules leading toward the compact equipment enclosure | Image metadata |
| FR001-S05 | `sources/fr001/FR001-S05_equipment-shelter_2026-07-25_1724.jpg` | Open wooden equipment shelter beside the array | Image metadata |
| FR001-S06 | `sources/fr001/FR001-S06_array-boulders_2026-07-26_1715.jpg` | Several fixed panel mounts below the surrounding boulder formations | Image metadata |

### Public captions derived from these sources

- **The setting:** Ground-mounted panels and the working area within the surrounding desert landscape.
- **Array and shelter:** Ground-mounted modules lead toward the compact wooden equipment enclosure.
- **Panels among the boulders:** Multiple fixed ground mounts follow the slope below the rock formations.
- **Equipment shelter:** Power electronics are kept in a small wooden enclosure beside the array.
- **Instrument reading:** At 4:10 p.m. the battery was at 79% charge, discharging lightly, with 213.4 amp-hours remaining.

### Photographs still needed

- Complete battery bank
- JK-BMS hardware and sensing leads
- Clear equipment-label photographs
- Full electrical protection and disconnect arrangement

## Unresolved questions

1. Exact OutBack charge-controller model.
2. Present array wiring and protection; earlier notes indicate two strings of three.
3. Loads active at 4:10 PM.
4. Location of the temperature sensor reporting 39.0 °C.
5. Whether BMS capacity should remain 270 Ah or match the 280 Ah cell rating.

## Field Report editorial rule

Observe first. Preserve exact readings. Keep interpretation brief. Do not
explain general solar theory unless a later report is specifically created for
that purpose.

## Revision log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-07-31 | Workbook created; FR001 opened; JK-BMS screenshot and readings attached. |
| 0.2 | 2026-08-03 | Five additional photographs cataloged; FR001 website captions and image sequence recorded. |
