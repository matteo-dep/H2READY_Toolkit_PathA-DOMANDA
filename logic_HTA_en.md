## ⚙️ How the assessment engine reasons

The tool does not simply look for companies that "use high temperatures". It crosses the **NACE code** with the **European RED III Directive** and the **laws of thermodynamics** to identify where hydrogen is *chemically irreplaceable* and where it would instead be a waste compared to direct electrification.

> **Guiding principle:** hydrogen *only* where electrification is not otherwise possible.

---

### 🔢 Reading the code (4 digits)

The engine reads **only the first 4 digits** of the code (the *Class*), removing dots and ignoring the trailing digits, which serve purely statistical purposes.

- Example: `24.10` → `2410` (Steel)
- If the code is not in the H2 priority database, the tool falls back to the **macro-sector** (first 2 digits) and raises an **alert** asking you to verify the data.

---

### 🚦 Thermodynamic verdicts

| Verdict | Meaning | Typical examples |
| :--- | :--- | :--- |
| 🟢 **Absolutely Necessary** | H2 as feedstock or reducing agent. No alternative. | Fertilizers/ammonia, organic chemicals, DRI steel |
| 🟢 **Necessary (physical limits)** | Large melting furnaces where energy density prevents mass electrification. | Flat and hollow glass |
| 🟡 **Optional / Competition** | Sectors where hydrogen competes at a disadvantage with Biomethane and SRF. | Cement, lime, refractories, bricks |
| 🟠 **Electrification Alert** | Heat treatments where induction or electric furnaces are more efficient than H2. | Cold drawing, forging, coating, general metallurgy |
| 🔴 **Thermodynamic Waste** | Steam/energy production, construction, data centers, by-product H2. | Steam, grid power, SMR, coke ovens |

---

### 🧮 Score calculation

Multipliers and bonuses are applied to the sector base score:

1. **Company size**
   - Large → ×1.5
   - Medium → ×1.2
   - Small → ×1.0
2. **Enabling bonuses** (additive)
   - IED permit present → **+2**
   - Located in Industrial Zone / consortium → **+3**
   - Proximity to the South H2 Corridor → **+3**

A high score indicates a priority candidate for a hydrogen action plan.

---

### 📝 Filling in the file (golden rule)

- **Mandatory:** `company name`, `nace code`, `size`.
- **Recommended:** `process`, `notes`, `location`, `IED`. The tool reads the text in *process* and *notes* to recover borderline companies (e.g. words like "DRI", "furnace", "melting") or to exclude false positives (e.g. by-product H2 from steam cracking).
