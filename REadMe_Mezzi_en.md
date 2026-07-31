## What this tool is for

The simulator answers three questions, in this order:

1. **Is it physically feasible?** How much does the battery needed for the mission weigh, and does it recharge within the available standstill window?
2. **How much more does it cost than diesel?** This is the figure required for a call for funding or a grant application.
3. **What does the territory need?** How many MWh per year, how many tonnes of hydrogen, how much renewable capacity behind it.

The verdict appears **at the top**, before the charts: if a technology fails the physical constraints, the economic comparison is pointless.

---

## Where the data comes from

Consumption, range, purchase and maintenance costs derive from the project database *Comparison H2 elc FF.xlsx* (averages of the market models surveyed), now embedded in the code: the tool runs without external attachments.

Battery, payload and service-life parameters come from the project literature, in particular the **Roland Berger report "Hydrogen trucks" (2021)** and experimental studies on cells at low temperature (*Energies* 2023, 16, 7142; *Energy Engineering* 2025, 122(9)).

---

## Core quantities

| Item | Unit | Meaning |
|---|---|---|
| `cons_kwh` | kWh/km | energy on board the vehicle per kilometre |
| `aut` | km | catalogue range under standard conditions |
| `maint` | €/km | maintenance |
| `capex` | € | purchase price |
| `dpay` | t | payload loss compared with diesel |

Consumption is expressed in **energy** for all technologies. Natural units (litres, kg, kWh) are obtained by dividing by the energy content of the carrier:

| Carrier | kWh per unit |
|---|---|
| Petrol | 8.76 kWh/l |
| Diesel | 9.91 kWh/l |
| Hydrogen | 33.33 kWh/kg |
| Electricity | 1.00 kWh/kWh |

These are real lower heating values: diesel at 9.91 against a physical value of 9.94, hydrogen exact at 33.33.

---

## Battery sizing

The battery is **not** a catalogue figure: it is sized on the mission.

```
capacity = daily km × corrected consumption × 1.33
```

The 1.33 coefficient is the Roland Berger margin: 90% of the state of charge is used so as not to degrade the pack, plus a 20% range reserve.

All physical metrics follow from this:

```
battery weight  = capacity ÷ energy density
charging time   = capacity ÷ available charging power
actual range    = capacity ÷ corrected consumption
```

**Weight limit.** If the required battery exceeds the maximum admissible, it is capped and the tool flags it. The maximum is the sum of three items: the vehicle's tolerance to payload loss, the **EU derogation of 2,000 kg** for zero-emission vehicles (Regulation (EU) 2019/1242), and the weight of the diesel powertrain saved. When the battery is capped two things can happen: the range still covers the day but without a safety margin, or it does not, in which case part of the energy must be bought at public charging.

---

## Operating conditions

Orography and climate correct consumption, **but not in the same way for every technology**. This is the point that earlier versions got wrong: applying the same multiplier to all of them cancelled the effect in the comparison.

### Gradients

| Route | Multiplier |
|---|---|
| Flat | ×1.00 |
| Hilly | ×1.15 |
| Mountain | ×1.35 |

Electric-drive vehicles — **both battery and fuel cell** — recover energy downhill through regenerative braking: 25% of the gradient penalty is cancelled for them.

### Harsh winter climate (< 0 °C)

| Technology | Multiplier |
|---|---|
| Diesel / Petrol | ×1.05 |
| Hydrogen (FCEV) | ×1.10 |
| Electric (BEV) | ×1.25 |

The difference has a precise physical reason: combustion engines and fuel cells heat the cabin with **waste heat** they would otherwise discard. A battery vehicle must produce it from electricity taken away from traction. On top of this comes the cell's loss of performance in the cold, which experimental studies quantify between 6% and 20% from 0 to −20 °C, with strong dependence on discharge current.

---

## Battery life

The pack **does not last as long as the vehicle**. Roland Berger estimates 1,400,000 km for the diesel engine, e-drive, fuel cell and hydrogen tanks, but only **700,000 km for the battery** (about 1,400 cycles when charging every 500 km).

```
replacements = ceil(total lifetime km ÷ battery life) − 1
```

The replacement cost appears as the **fourth bar** in the TCO chart.

**Cold shortens the life of the pack**, not just its range. At low temperature metallic lithium is deposited on the anode (*lithium plating*): the SEI film thickens, internal resistance grows and in the worst cases an internal short circuit develops. With a harsh climate the tool reduces service life by 25%.

---

## Payload

For freight vehicles a comparison in €/km is **misleading**: an electric truck that costs less per kilometre but carries three tonnes less requires more trips. This is why **€/tonne-km** is also computed.

Payload loss is calculated differently for the two technologies:

- **Electric**: from the battery actually required by the mission, net of the EU derogation and the powertrain saved. It therefore varies with distance, orography and climate.
- **Hydrogen**: literature value (Roland Berger), from −1.53 t to −1.90 t for heavy vehicles at 700 bar.

---

## Learning curves

The purchase-year slider (2024-2035) linearly interpolates:

| Parameter | 2024 | 2030 |
|---|---|---|
| Battery energy density | 0.176 kWh/kg | 0.233 kWh/kg |
| Battery cost | 167 €/kWh | 161 €/kWh |
| Fuel cell cost | 330 €/kW | 210 €/kW |
| Hydrogen range | reference | +15% |

Carrier prices follow the trends set in the sidebar: diesel ×1.1, electricity ×0.9, grid hydrogen ×0.6, self-produced hydrogen ×0.7. These are consistent with the Roland Berger projections, which for hydrogen at 700 bar indicate a move from 7.30 €/kg in 2023 to 4.80 €/kg in 2030.

---

## Emissions and efficiency

Emissions are calculated over the **life cycle**, adding vehicle manufacturing to the well-to-wheel emissions of the energy carrier:

| Carrier | kg CO₂ per kWh on board |
|---|---|
| Petrol | 0.330 |
| Diesel | 0.307 |
| Grid electricity | 0.215 |
| Self-produced electricity | 0.055 |
| Grid hydrogen | 0.387 |
| Self-produced hydrogen | 0.090 |

These factors are **internally consistent**: self-produced hydrogen (0.090) is derived from photovoltaics by multiplying 0.055 kg/kWh by the 55 kWh needed to produce one kilogram of hydrogen and dividing by its energy content. The 55 kWh/kg imply an electrolysis efficiency of 60.6%, within the real range.

The well-to-wheel efficiency shown in chart C is the product of two efficiencies: that of the supply chain (from primary source to energy on board) and that of the powertrain (from energy on board to the wheel: 40% for a combustion engine, 88% for an electric one, 52% for a fuel cell).

---

## What to change, and where

| What | Where in the code |
|---|---|
| Consumption, range, costs, payload | `VEICOLI` dictionary |
| Energy content of carriers | `CONV` |
| Emission factors | `F_EMISS` |
| Supply-chain and powertrain efficiencies | `WTT`, `TTW` |
| Gradient penalty | `ORO` |
| Regenerative braking recovery | `REGEN` |
| Climate penalties | `FREDDO` |
| Battery life and cold degradation | `BATT_VITA_KM`, `VITA_FREDDO` |
| Pack sizing margin | `BATT_BUFFER` |
| Weight derogation and powertrain saved | `DEROGA_UE_KG`, `POWERTRAIN_RISPARMIATO_KG` |

---

## Known limitations

The model **does not include the cost of carbon**. Road transport entered the ETS II system on 1 January 2025, with the market phase from 2027: once that cost is passed on to the price of diesel, the comparison will shift in favour of the alternatives. Likewise, road-toll differentiation for zero-emission vehicles is not considered.

Charging and refuelling infrastructure costs are not included and must be added separately: from €2,000 for a slow wallbox to over €80,000 for an ultra-fast charging point for heavy vehicles, and from €1 million to over €3 million for a high-pressure hydrogen station (see Tool 2.8).

Payload-loss values for buses and cars are estimates; those for heavy vehicles come from the literature.
