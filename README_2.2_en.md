## What this tool does

It compares, **for the same distance driven**, how much a fleet costs and pollutes when running
on diesel/petrol, on batteries (BEV) or on hydrogen (FCEV). It does not decide for you: it shows
the figures and the conditions under which one technology becomes preferable to another.

Results are **annual** and refer to the whole fleet, not to a single vehicle.

---

## Where the data comes from

The technical and economic values are embedded in the code and derive from the
`AUTO`, `CAMION`, `AUTOBUS Urbano` and `AUTOBUS ExtraUrbano` sheets of *Comparison H2 elc FF.xlsx*,
as the **average of the market models surveyed**. For each vehicle/powertrain combination:

| Item | Unit | What it represents |
|---|---|---|
| `cons` | l/km · kWh/km · kg/km | consumption under standard conditions |
| `prim` | kWh/km | primary energy (well-to-wheel) |
| `wtt` | kg CO₂/km | supply-chain emissions of the energy carrier |
| `ttw` | kg CO₂/km | tailpipe emissions |
| `constr` | kg CO₂ | vehicle manufacturing emissions (total, spread over the years) |
| `maint` | €/km | maintenance |
| `capex` | € | vehicle purchase price |
| `range` | km | declared range under standard conditions |

> **Range:** the `range` values are market estimates added to make the leg check possible.
> They are the only data **not** derived from the original Excel file: they should be verified
> and aligned with the project's reference models.

---

## How it is calculated

With `km_tot = number of vehicles × km/year per vehicle`:

**Costs (€/year)**
```
fuel         = corrected_consumption × km_tot × price
maintenance  = maint × km_tot
purchase     = capex × number of vehicles ÷ lifetime
TCO          = fuel + maintenance + purchase
€/km         = TCO ÷ km_tot
```
The purchase cost is **spread over the years of service**: a longer lifetime lowers the annual cost.

**Emissions (t CO₂/year)**
```
supply chain (WtT) = wtt × corrected/base consumption × km_tot ÷ 1000
tailpipe (TtW)     = ttw × corrected/base consumption × km_tot ÷ 1000
manufacturing      = constr × number of vehicles ÷ lifetime ÷ 1000
```
Vehicle manufacturing does **not** depend on operating conditions; the other two do, because
they follow actual consumption.

---

## Operating conditions

Three parameters correct the standard consumption. The resulting multiplier acts on fuel,
in-use emissions and primary energy — and inversely on range.

### Orography

| Route | Multiplier |
|---|---|
| Flat | ×1.00 |
| Hilly | ×1.15 |
| Mountain | ×1.35 |

Vehicles with an electric drivetrain (**both BEV and FCEV**) recover energy downhill through
regenerative braking: for them **25%** of the gradient penalty is cancelled. In the mountains a
diesel takes ×1.35, an electric vehicle ×1.26.

### Climate

Cold does not penalise everyone equally. Heating the cabin of a BEV draws energy from the
battery, and at low temperature the cell chemistry performs worse. Diesel engines and fuel cells
heat the cabin with **waste heat** they would otherwise throw away.

| Climate | Thermal (diesel/petrol) | Hydrogen (FCEV) | Battery (BEV) |
|---|---|---|---|
| Mild (> 10 °C) | ×1.00 | ×1.00 | ×1.00 |
| Temperate (0–10 °C) | ×1.02 | ×1.03 | ×1.08 |
| Harsh (< 0 °C) | ×1.05 | ×1.10 | ×1.25 |

### Longest leg without a stop

This is the maximum distance the vehicle must cover before it can stop. It is compared with the
**derated range** (`range ÷ multiplier`), because uphill and in the cold the real range drops:

| Leg/range ratio | Outcome |
|---|---|
| ≤ 0.8 | 🟢 Leg covered |
| 0.8 – 1.0 | 🟡 Tight margin |
| > 1.0 | 🔴 Stop required |

The traffic light is **informative, not economic**: it does not change the TCO. It exists to show
when an option that looks cheaper on paper is **operationally impractical** — the typical case of
a BEV on long-haul duty, where a recharging stop costs hours of service.

---

## Important note on prices

All carrier prices are on an **"at the pump"** basis: they include distribution, compression to
700 bar for hydrogen, and station margins.

Do not confuse them with **production costs**, which are a different quantity: grey hydrogen from
methane reforming costs around 2 €/kg *at the plant gate*, but five times as much once dispensed
at a station. In earlier versions of this tool the default value for grey hydrogen was precisely
the production cost (2 €/kg), which made it come out **cheaper than diesel** — an accounting
artefact, not a result.

The current default is **10 €/kg** dispensed. If you want to work with production costs, you must
realign **all** carriers on the same basis, not hydrogen alone.

---

## How to read the results

Cards are **numbered** according to the sorting selected (cost, emissions or €/km), so "1" is
always the best option with respect to the criterion currently active.

In the metric bars, **colour** tells whether the value is good (green) or problematic (red), and
**length** shows its size relative to the other powertrains. For costs, emissions and energy the
rule is always: shorter is better.

The two badges mark the **cheapest** and the **cleanest** option: when they do not coincide, the
choice is a trade-off that needs to be justified — and that is exactly where the action plan
comes in.

---

## What to change, and where

| What | Where in the code |
|---|---|
| Consumption, costs, emissions, ranges | `VEHICLES` dictionary |
| Default carrier prices | `FUEL_DEFAULTS` |
| Gradient penalty | `ORO_MULT` |
| Regenerative braking recovery | `REGEN_SHARE` |
| Climate penalties per powertrain | `TEMP_MULT` |
| Range traffic-light thresholds | `valuta_tratta` function |

The orography and climate multipliers are **project parameters, not measurements**: they are
orders of magnitude consistent with the literature on electric vehicles in cold climates and on
routes with gradients. They should be revised if the project adopts its own values.
