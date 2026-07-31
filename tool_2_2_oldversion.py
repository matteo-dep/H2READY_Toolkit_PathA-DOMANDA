import streamlit as st
import pandas as pd
import math
import os

# ==========================================================================
# H2READY TOOLKIT · Tool 2.2 — Confronto flotte Diesel / BEV / FCEV
#
# VERSIONE UNIFICATA: motore di calcolo rigoroso (TCO, LCA, split di prezzo
# deposito/viaggio, soste e fermo) + matrice decisionale a semafori.
#
# NOVITA' RISPETTO ALLA v1, tutte derivate dalla letteratura di progetto:
#  1. CARICO UTILE. I mezzi a batteria e a idrogeno perdono payload. Il
#     confronto passa da €/km a €/tonnellata-km per i mezzi merci.
#     Fonte: Roland Berger, "Camion a idrogeno" (2021), tabelle payload.
#     Deroga UE: Direttiva 2015/719 (+1 t combustibili alternativi),
#     Regolamento 2019/1242 (+2 t veicoli a zero emissioni).
#  2. SOSTITUZIONE BATTERIA. Vita batteria ~700.000 km contro 1.400.000 km
#     di motore diesel, e-drive, fuel cell e serbatoi H2 (Roland Berger).
#     Oltre quella soglia il pacco va sostituito: costo che prima mancava.
#  3. DEGRADO DA FREDDO. Il lithium plating a bassa temperatura accorcia la
#     vita del pacco, non solo l'autonomia (Energies 2023 16:7142;
#     Energy Eng. 2025 122(9) su celle LFP).
#  4. CURVE DI APPRENDIMENTO. Slider anno 2024-2035 che interpola prezzi dei
#     vettori, densità e costo della batteria.
# ==========================================================================

st.set_page_config(page_title="H2READY · Tool 2.2 Flotte", page_icon="🚚", layout="wide")

# ==========================================================================
# 1. LINGUA (struttura multilingua predisposta; EN/SL ricadono su IT)
# ==========================================================================
LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]
if LANG != "it":
    st.sidebar.caption("⚠️ Traduzione in corso: contenuti mostrati in italiano.")
    LANG = "it"

# ==========================================================================
# 2. DATI TECNICO-ECONOMICI
#    cons   consumo [l/km · kWh/km · kg/km]      prim   energia primaria [kWh/km]
#    wtt    filiera [kg CO2/km]                  ttw    scarico [kg CO2/km]
#    constr produzione veicolo [kg CO2]          maint  manutenzione [€/km]
#    capex  prezzo d'acquisto [€]                range  autonomia standard [km]
#    dpay   perdita di carico utile vs diesel [t], già al netto della deroga UE
# ==========================================================================
VEHICLES = {
    "auto": {
        "icon": "🚗", "life": 12, "km_default": 15000, "km_max": 60000,
        "tratta_default": 150, "tratta_max": 1200, "charge_kw": 100,
        "payload_t": 0.4, "merci": False,
        "vectors": {
            "benzina":  {"unit": "l",   "cons": 0.067250, "prim": 0.6925, "wtt": 0.03884, "ttw": 0.15535, "constr": 6000,  "maint": 0.0800, "capex": 41000, "range": 800, "dpay": 0.00},
            "diesel":   {"unit": "l",   "cons": 0.054000, "prim": 0.6147, "wtt": 0.02138, "ttw": 0.14256, "constr": 6000,  "maint": 0.0650, "capex": 45000, "range": 950, "dpay": 0.00},
            "elc_rete": {"unit": "kwh", "cons": 0.136667, "prim": 0.2733, "wtt": 0.02938, "ttw": 0.0, "constr": 12000, "maint": 0.0300, "capex": 38333, "range": 400, "dpay": 0.30},
            "elc_auto": {"unit": "kwh", "cons": 0.136667, "prim": 0.1519, "wtt": 0.00752, "ttw": 0.0, "constr": 12000, "maint": 0.0300, "capex": 38333, "range": 400, "dpay": 0.30},
            "h2_rete":  {"unit": "kg",  "cons": 0.010000, "prim": 1.2120, "wtt": 0.12900, "ttw": 0.0, "constr": 14000, "maint": 0.0550, "capex": 67500, "range": 600, "dpay": 0.15},
            "h2_verde": {"unit": "kg",  "cons": 0.010000, "prim": 0.5376, "wtt": 0.03000, "ttw": 0.0, "constr": 14000, "maint": 0.0550, "capex": 67500, "range": 600, "dpay": 0.15},
        }},
    "truck": {
        "icon": "🚛", "life": 7, "km_default": 170000, "km_max": 300000,
        "tratta_default": 500, "tratta_max": 1500, "charge_kw": 350,
        "payload_t": 24.0, "merci": True,
        "vectors": {
            "diesel":   {"unit": "l",   "cons": 0.330000, "prim": 3.7563,  "wtt": 0.13068, "ttw": 0.87120, "constr": 60000,  "maint": 0.2500, "capex": 115000, "range": 1400, "dpay": 0.00},
            "elc_rete": {"unit": "kwh", "cons": 1.572500, "prim": 3.1450,  "wtt": 0.33809, "ttw": 0.0, "constr": 110000, "maint": 0.1400, "capex": 245000, "range": 400, "dpay": 3.30},
            "elc_auto": {"unit": "kwh", "cons": 1.572500, "prim": 1.7472,  "wtt": 0.08649, "ttw": 0.0, "constr": 110000, "maint": 0.1400, "capex": 245000, "range": 400, "dpay": 3.30},
            "h2_rete":  {"unit": "kg",  "cons": 0.084167, "prim": 10.2010, "wtt": 1.08575, "ttw": 0.0, "constr": 125000, "maint": 0.2000, "capex": 400000, "range": 800, "dpay": 1.53},
            "h2_verde": {"unit": "kg",  "cons": 0.084167, "prim": 4.5246,  "wtt": 0.25250, "ttw": 0.0, "constr": 125000, "maint": 0.2000, "capex": 400000, "range": 800, "dpay": 1.53},
        }},
    "bus_u": {
        "icon": "🚌", "life": 13, "km_default": 70000, "km_max": 150000,
        "tratta_default": 200, "tratta_max": 600, "charge_kw": 150,
        "payload_t": 6.0, "merci": False,
        "vectors": {
            "diesel":   {"unit": "l",   "cons": 0.386667, "prim": 4.4014,  "wtt": 0.15312, "ttw": 1.02080, "constr": 50000, "maint": 0.3250, "capex": 213333, "range": 600, "dpay": 0.00},
            "elc_rete": {"unit": "kwh", "cons": 1.677500, "prim": 3.3550,  "wtt": 0.36066, "ttw": 0.0, "constr": 85000, "maint": 0.1600, "capex": 397500, "range": 250, "dpay": 1.50},
            "elc_auto": {"unit": "kwh", "cons": 1.677500, "prim": 1.8639,  "wtt": 0.09226, "ttw": 0.0, "constr": 85000, "maint": 0.1600, "capex": 397500, "range": 250, "dpay": 1.50},
            "h2_rete":  {"unit": "kg",  "cons": 0.096333, "prim": 11.6756, "wtt": 1.24270, "ttw": 0.0, "constr": 95000, "maint": 0.2750, "capex": 566667, "range": 400, "dpay": 0.80},
            "h2_verde": {"unit": "kg",  "cons": 0.096333, "prim": 5.1787,  "wtt": 0.28900, "ttw": 0.0, "constr": 95000, "maint": 0.2750, "capex": 566667, "range": 400, "dpay": 0.80},
        }},
    "bus_x": {
        "icon": "🚍", "life": 15, "km_default": 75000, "km_max": 150000,
        "tratta_default": 300, "tratta_max": 900, "charge_kw": 150,
        "payload_t": 6.0, "merci": False,
        "vectors": {
            "diesel":   {"unit": "l",   "cons": 0.283333, "prim": 3.2251, "wtt": 0.11220, "ttw": 0.85977, "constr": 50000, "maint": 0.2300, "capex": 227500, "range": 800, "dpay": 0.00},
            "elc_rete": {"unit": "kwh", "cons": 1.166667, "prim": 2.3333, "wtt": 0.25083, "ttw": 0.0, "constr": 85000, "maint": 0.1350, "capex": 450000, "range": 300, "dpay": 1.80},
            "elc_auto": {"unit": "kwh", "cons": 1.166667, "prim": 1.2963, "wtt": 0.06417, "ttw": 0.0, "constr": 85000, "maint": 0.1350, "capex": 450000, "range": 300, "dpay": 1.80},
            "h2_rete":  {"unit": "kg",  "cons": 0.065833, "prim": 7.9790, "wtt": 0.84925, "ttw": 0.0, "constr": 95000, "maint": 0.2200, "capex": 675000, "range": 500, "dpay": 0.90},
            "h2_verde": {"unit": "kg",  "cons": 0.065833, "prim": 3.5391, "wtt": 0.19750, "ttw": 0.0, "constr": 95000, "maint": 0.2200, "capex": 675000, "range": 500, "dpay": 0.90},
        }},
}

VEH_LBL = {"auto": "Auto / veicoli leggeri", "truck": "Camion pesanti",
           "bus_u": "Autobus urbano", "bus_x": "Autobus extraurbano"}
VEC_LBL = {"benzina": "Benzina", "diesel": "Diesel", "elc_rete": "Elettrico (rete)",
           "elc_auto": "Elettrico (autoprodotto)", "h2_rete": "Idrogeno da rete",
           "h2_verde": "Idrogeno verde autoprodotto"}
VEC_ICON = {"benzina": "⛽", "diesel": "⛽", "elc_rete": "⚡", "elc_auto": "🔆",
            "h2_rete": "💧", "h2_verde": "💧"}
UNIT_LBL = {"benzina": "€/l", "diesel": "€/l", "elc_rete": "€/kWh", "elc_auto": "€/kWh",
            "h2_rete": "€/kg", "h2_verde": "€/kg"}
CONS_LBL = {"l": "l/km", "kwh": "kWh/km", "kg": "kg/km"}
FAM_LBL = {"ice": "⛽ Diesel / Benzina", "bev": "⚡ Elettrico (BEV)", "fcev": "💧 Idrogeno (FCEV)"}
FAM_COL = {"ice": "#A33B4A", "bev": "#0D7C5C", "fcev": "#1C7C8C"}

def famiglia(vk):
    if vk in ("benzina", "diesel"):
        return "ice"
    return "bev" if vk.startswith("elc") else "fcev"

# ==========================================================================
# 3. CURVE DI APPRENDIMENTO (ancoraggi da letteratura, interpolazione lineare)
#    Roland Berger 2021, "Camion a idrogeno" — assunzioni energia/batteria.
# ==========================================================================
BATT_DENSITY = {2023: 0.176, 2027: 0.199, 2030: 0.233}   # kWh/kg pacco grande
BATT_COST    = {2023: 167.0, 2027: 157.0, 2030: 161.0}   # €/kWh scenario "rather mass"

# Scenario A — mercato italiano attuale (prezzi costanti, modificabili a mano)
PREZZI_IT = {"benzina": 1.90, "diesel": 1.80, "elc_rete": 0.31, "elc_auto": 0.24,
             "h2_rete": 20.00, "h2_verde": 15.00}
# Scenario B — proiezione Roland Berger (fornitura industriale su larga scala)
PREZZI_RB = {
    "benzina":  {2023: 1.26, 2027: 1.37, 2030: 1.37},
    "diesel":   {2023: 1.26, 2027: 1.37, 2030: 1.37},
    "elc_rete": {2023: 0.30, 2027: 0.20, 2030: 0.24},
    "elc_auto": {2023: 0.24, 2027: 0.16, 2030: 0.19},   # -20% autoproduzione
    "h2_rete":  {2023: 7.30, 2027: 5.74, 2030: 4.80},   # 700 bar
    "h2_verde": {2023: 6.90, 2027: 5.40, 2030: 4.50},   # 350 bar / in situ
}
# Rincaro dell'energia acquistata in viaggio rispetto al deposito
ROAD_MARKUP = {"benzina": 1.03, "diesel": 1.03, "elc_rete": 2.26,
               "elc_auto": 2.92, "h2_rete": 1.00, "h2_verde": 1.33}

def interp(anno, ancore):
    """Interpolazione lineare tra ancoraggi; costante fuori dall'intervallo."""
    anni = sorted(ancore)
    if anno <= anni[0]:
        return ancore[anni[0]]
    if anno >= anni[-1]:
        return ancore[anni[-1]]
    for a, b in zip(anni, anni[1:]):
        if a <= anno <= b:
            f = (anno - a) / (b - a)
            return ancore[a] + (ancore[b] - ancore[a]) * f
    return ancore[anni[-1]]

# --- Condizioni di impiego ------------------------------------------------
ORO_MULT = {"pianura": 1.00, "collina": 1.15, "montagna": 1.35}
REGEN_SHARE = 0.25
TEMP_MULT = {"ice":  {"mite": 1.00, "temperato": 1.02, "rigido": 1.05},
             "fcev": {"mite": 1.00, "temperato": 1.03, "rigido": 1.10},
             "bev":  {"mite": 1.00, "temperato": 1.08, "rigido": 1.25}}
# Il freddo accorcia la vita del pacco (lithium plating): fattore su km utili
TEMP_LIFE = {"mite": 1.00, "temperato": 0.90, "rigido": 0.75}
BATT_LIFE_KM = 700_000       # Roland Berger: ~1.400 cicli con ricarica ogni 500 km
REFUEL_MIN = {"ice": 10.0, "fcev": 15.0}
RECHARGE_SOC = 0.80

# ==========================================================================
# 4. STILE
# ==========================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap');
.h2-sub { opacity:.7; font-size:.96rem; margin:-4px 0 2px 0; }
.h2-recap { font-size:.82rem; opacity:.6; margin:6px 0 0 0; }
.h2-take { background:rgba(13,124,92,.13); border:1px solid rgba(13,124,92,.40);
           border-left:6px solid #0D7C5C; border-radius:12px; padding:15px 19px; margin:16px 0 8px 0; font-size:1rem; }
.h2-take b { font-weight:700; }
.h2-note { opacity:.6; font-size:.8rem; margin:8px 0 4px 0; }
table.h2t { width:100%; border-collapse:collapse; font-size:.85rem; margin:4px 0 16px 0; }
table.h2t th { font-size:.68rem; text-transform:uppercase; letter-spacing:.04em; opacity:.55;
               font-weight:600; padding:7px 10px; border-bottom:1px solid rgba(127,127,127,.30); text-align:center; }
table.h2t th:first-child { text-align:left; }
table.h2t td { padding:9px 10px; border-bottom:1px solid rgba(127,127,127,.15); text-align:center;
               font-family:'Space Grotesk',sans-serif; }
table.h2t td.k { text-align:left; font-family:inherit; font-weight:600; }
table.h2t td small { display:block; opacity:.55; font-weight:500; font-size:.68rem; font-family:inherit; }
table.h2t tr:last-child td { border-bottom:none; }
.sem { display:inline-block; padding:3px 10px; border-radius:11px; color:#fff;
       font-size:.7rem; font-weight:700; font-family:'Space Grotesk',sans-serif; letter-spacing:.03em; }
.h2-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:13px; margin:6px 0 14px 0; }
.h2c { background:rgba(127,127,127,.09); border:1px solid rgba(127,127,127,.24);
       border-left-width:6px; border-radius:12px; padding:14px 16px; }
.h2c-h { font-weight:700; font-size:1rem; margin-bottom:3px; }
.h2c-s { font-size:.76rem; opacity:.6; margin-bottom:10px; }
.h2c-r { display:flex; justify-content:space-between; font-size:.82rem; padding:3px 0; }
.h2c-r b { font-family:'Space Grotesk',sans-serif; }
.h2b-row { display:grid; grid-template-columns:210px 1fr 125px; align-items:center; gap:11px; margin-bottom:8px; }
.h2b-label { font-size:.82rem; font-weight:600; text-align:right; }
.h2b-track { display:flex; height:23px; border-radius:6px; overflow:hidden;
             background:rgba(127,127,127,.18); border:1px solid rgba(127,127,127,.26); }
.h2b-seg { height:100%; display:flex; align-items:center; justify-content:center; color:#fff;
           font-size:.68rem; font-weight:700; font-family:'Space Grotesk',sans-serif; overflow:hidden;
           text-shadow:0 1px 1px rgba(0,0,0,.45); }
.h2b-total { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.92rem; }
.h2b-total small { opacity:.55; font-weight:500; font-size:.65rem; }
.h2-leg { display:flex; flex-wrap:wrap; gap:13px; margin-bottom:10px; }
.h2-leg span { display:flex; align-items:center; gap:6px; font-size:.77rem; opacity:.85; }
.h2-leg i { width:12px; height:12px; border-radius:3px; display:inline-block; }
@media (max-width:560px){ .h2b-row{ grid-template-columns:110px 1fr 88px; } }
</style>
"""

# ==========================================================================
# 5. SIDEBAR
# ==========================================================================
st.sidebar.markdown("### 🎯 La tua flotta")
veh_map = {VEH_LBL[k]: k for k in VEHICLES}
veh_choice = st.sidebar.selectbox("Tipo di veicolo", list(veh_map.keys()))
VEH = veh_map[veh_choice]
vd = VEHICLES[VEH]

n_mezzi = st.sidebar.number_input("Numero di veicoli", 1, 500, 5, 1)
km_anno = st.sidebar.slider("Chilometri all'anno per veicolo", 1000, vd["km_max"],
                            vd["km_default"], 1000)
lifetime = st.sidebar.slider("Durata del veicolo [anni]", 1, 30, vd["life"], 1)

st.sidebar.markdown("### 🏔️ Condizioni di impiego")
ORO = st.sidebar.selectbox("Orografia del percorso", list(ORO_MULT.keys()),
                           format_func=lambda k: k.capitalize(),
                           help="Le pendenze aumentano il consumo. I mezzi elettrici e a idrogeno "
                                "recuperano parte dell'energia in discesa, quindi la penalità è ridotta.")
TEMP = st.sidebar.selectbox("Clima medio della zona", list(TEMP_MULT["bev"].keys()), index=1,
                            format_func=lambda k: {"mite": "Mite (> 10 °C)",
                                                   "temperato": "Temperato (0–10 °C)",
                                                   "rigido": "Rigido (< 0 °C)"}[k],
                            help="Il freddo penalizza le batterie due volte: consumano di più "
                                 "(riscaldamento abitacolo) e invecchiano più in fretta (lithium plating).")
tratta = st.sidebar.slider("Tratta più lunga senza sosta [km]", 10, vd["tratta_max"],
                           vd["tratta_default"], 10,
                           help="Oltre l'autonomia il mezzo deve fermarsi e comprare energia "
                                "a prezzo pubblico. È il parametro che ribalta il confronto.")

st.sidebar.markdown("### 📅 Scenario temporale")
anno = st.sidebar.slider("Anno di acquisto della flotta", 2024, 2035, 2026, 1,
                         help="Sposta prezzi dei vettori, densità e costo della batteria "
                              "lungo le curve di apprendimento.")
scenario = st.sidebar.radio("Base dei prezzi",
                            ["Mercato attuale (IT)", "Proiezione Roland Berger"],
                            help="Il mercato italiano di oggi riflette il distributore al dettaglio. "
                                 "La proiezione Roland Berger ipotizza fornitura industriale su larga "
                                 "scala per flotte: l'idrogeno costa 2-3 volte meno.")
SCEN = "it" if scenario.startswith("Mercato") else "rb"

st.sidebar.markdown("### 🏗️ Infrastruttura disponibile")
infra_h2 = st.sidebar.selectbox("Stazione H2 entro 15 km", ["Assente", "Pianificata", "Esistente"])
infra_el = st.sidebar.selectbox("Rete elettrica al deposito",
                                ["Adeguata", "Da potenziare", "Insufficiente"])

# --- Prezzi (precompilati dallo scenario, sempre modificabili) -------------
dens_batt = interp(anno, BATT_DENSITY)
costo_batt = interp(anno, BATT_COST)

prezzi, prezzi_road = {}, {}
with st.sidebar.expander("💶 Prezzi dei vettori", expanded=False):
    st.caption("Due prezzi: **deposito** (il mezzo parte pieno) e **in viaggio** "
               "(colonnina o stazione pubblica). Precompilati dallo scenario e dall'anno.")
    for vk in vd["vectors"]:
        base = PREZZI_IT[vk] if SCEN == "it" else interp(anno, PREZZI_RB[vk])
        st.markdown(f"**{VEC_LBL[vk]}** [{UNIT_LBL[vk]}]")
        ca, cb = st.columns(2)
        prezzi[vk] = ca.number_input("deposito", value=round(float(base), 2), format="%.2f",
                                     key=f"p_{vk}_{SCEN}_{anno}")
        prezzi_road[vk] = cb.number_input("in viaggio",
                                          value=round(float(base * ROAD_MARKUP[vk]), 2),
                                          format="%.2f", key=f"pr_{vk}_{SCEN}_{anno}")

with st.sidebar.expander("⚙️ Parametri avanzati", expanded=False):
    costo_fermo = st.number_input("Costo del fermo operativo [€/h]", 0.0, value=30.0, step=5.0,
                                  help="Autista, servizio non svolto, ritardo. Metti 0 per escluderlo.")
    costo_batt = st.number_input("Costo batteria [€/kWh]", 50.0, 400.0, float(round(costo_batt)), 5.0,
                                 help="Precompilato dalla curva Roland Berger per l'anno scelto.")
    batt_life = st.number_input("Vita utile batteria [km]", 200_000, 1_500_000, BATT_LIFE_KM, 50_000,
                                help="Roland Berger: ~700.000 km, contro 1.400.000 km di motore "
                                     "diesel, fuel cell e serbatoi H2.")
    if vd["merci"]:
        payload_nom = st.number_input("Carico utile nominale diesel [t]", 1.0, 40.0,
                                      float(vd["payload_t"]), 0.5)
        load_factor = st.slider("Fattore di riempimento medio [%]", 10, 100, 60) / 100.0
    else:
        payload_nom, load_factor = vd["payload_t"], 1.0

# ==========================================================================
# 6. MOTORE DI CALCOLO
# ==========================================================================
km_tot = n_mezzi * km_anno
km_vita = km_anno * lifetime

def mult_cond(fam):
    m = ORO_MULT[ORO]
    if fam in ("bev", "fcev"):
        m = 1.0 + (m - 1.0) * (1.0 - REGEN_SHARE)
    return m * TEMP_MULT[fam][TEMP]

def calcola(vk, v):
    fam = famiglia(vk)
    m = mult_cond(fam)
    cons_km = v["cons"] * m
    cons_tot = cons_km * km_tot
    range_eff = v["range"] / m

    # Dove si compra l'energia: pieno al deposito, il resto in viaggio
    share_road = max(0.0, tratta - range_eff) / tratta if tratta > 0 else 0.0
    p_eff = prezzi[vk] * (1 - share_road) + prezzi_road[vk] * share_road

    # Soste e fermo operativo
    stops_leg = max(0, math.ceil(tratta / range_eff) - 1) if range_eff > 0 else 0
    stops_year = stops_leg * (km_anno / tratta if tratta else 0) * n_mezzi
    batt_kwh = v["range"] * v["cons"] if fam == "bev" else 0.0
    stop_h = (batt_kwh * RECHARGE_SOC / vd["charge_kw"]) if fam == "bev" else REFUEL_MIN[fam] / 60.0
    down_h = stops_year * stop_h
    down_cost = down_h * costo_fermo

    # Sostituzione batteria (solo BEV): il freddo accorcia la vita utile
    life_km_eff = batt_life * TEMP_LIFE[TEMP]
    n_repl = max(0, math.ceil(km_vita / life_km_eff) - 1) if fam == "bev" else 0
    repl_year = (n_repl * batt_kwh * costo_batt * n_mezzi) / lifetime

    # Carico utile
    peso_batt_t = (batt_kwh / dens_batt) / 1000.0 if fam == "bev" else 0.0
    payload_eff = max(0.1, payload_nom - v["dpay"])

    # Costi
    fuel = cons_tot * p_eff
    maint = v["maint"] * km_tot
    capex = v["capex"] * n_mezzi / lifetime
    tco = fuel + maint + capex + down_cost + repl_year

    tkm = km_tot * payload_eff * load_factor
    return {
        "key": vk, "Nome": VEC_LBL[vk], "icon": VEC_ICON[vk], "fam": fam,
        "Consumo": cons_km, "unit": v["unit"],
        "Fuel": fuel, "Maint": maint, "CAPEx": capex, "Down": down_cost, "Repl": repl_year,
        "TCO": tco, "EurKm": tco / km_tot if km_tot else 0,
        "EurTkm": tco / tkm if tkm else 0,
        "WtT": v["wtt"] * m * km_tot / 1000, "TtW": v["ttw"] * m * km_tot / 1000,
        "Constr": v["constr"] * n_mezzi / lifetime / 1000,
        "Prim": v["prim"] * m * km_tot / 1000,
        "Range": range_eff, "ShareRoad": share_road, "PEff": p_eff,
        "StopsLeg": stops_leg, "StopH": stop_h, "DownH": down_h,
        "NRepl": n_repl, "PesoBatt": peso_batt_t, "DPay": v["dpay"], "PayEff": payload_eff,
    }

df = pd.DataFrame([calcola(vk, v) for vk, v in vd["vectors"].items()])
df["CO2"] = df["WtT"] + df["TtW"] + df["Constr"]
COSTO = "EurTkm" if vd["merci"] else "EurKm"
UNIT_COSTO = "€/t·km" if vd["merci"] else "€/km"

# ==========================================================================
# 7. HELPER
# ==========================================================================
def fmt(v, dec=0):
    return f"{v:,.{dec}f}".replace(",", "@").replace(".", ",").replace("@", ".")

SEM_COL = {"v": "#0D7C5C", "g": "#C98A1B", "r": "#A33B4A"}
SEM_TXT = {"v": "🟢 Verde", "g": "🟡 Giallo", "r": "🔴 Rosso"}

def sem(ok, warn):
    return "v" if ok else ("g" if warn else "r")

def badge(s):
    return f"<span class='sem' style='background:{SEM_COL[s]}'>{SEM_TXT[s]}</span>"

# Rappresentante di ogni famiglia = il vettore più economico della famiglia
rep = {}
for fam in ("ice", "bev", "fcev"):
    sub = df[df["fam"] == fam]
    if not sub.empty:
        rep[fam] = sub.loc[sub[COSTO].idxmin()]
FAMS = list(rep.keys())

# ==========================================================================
# 8. INTESTAZIONE E MESSAGGIO CHIAVE
# ==========================================================================
st.markdown(CSS, unsafe_allow_html=True)
st.title("🚚 Confronto flotte: Diesel, Elettrico e Idrogeno")
st.markdown("<div class='h2-sub'>Quanto costa, quanto inquina e soprattutto "
            "<b>quando una soluzione è davvero praticabile</b>.</div>", unsafe_allow_html=True)
st.caption("H2READY Toolkit · Tool 2.2 — sviluppato nel progetto "
           "[INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da "
           "**Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**")
st.markdown(f"<div class='h2-recap'>{n_mezzi} × {veh_choice} · {fmt(km_tot)} km/anno complessivi · "
            f"{ORO.capitalize()} · clima {TEMP} · tratta {fmt(tratta)} km · "
            f"acquisto {anno} · prezzi: {scenario}</div>", unsafe_allow_html=True)

readme = f"README_2.2_{LANG}.md"
with st.expander("ℹ️ Come funziona questo strumento (dati, formule, fonti)", expanded=False):
    if os.path.exists(readme):
        st.markdown(open(readme, encoding="utf-8").read())
    else:
        st.info(f"Metti il file `{readme}` nella stessa cartella per vedere qui la spiegazione.")

i_cheap = df[COSTO].idxmin()
i_clean = df["CO2"].idxmin()
st.markdown(
    f"<div class='h2-take'>Per {n_mezzi} <b>{veh_choice.lower()}</b> che percorrono "
    f"{fmt(km_anno)} km/anno su tratte fino a {fmt(tratta)} km, la soluzione "
    f"<b>più economica</b> è <b>{df.loc[i_cheap,'Nome']}</b> "
    f"({fmt(df.loc[i_cheap,COSTO], 3)} {UNIT_COSTO}) e la <b>più pulita</b> è "
    f"<b>{df.loc[i_clean,'Nome']}</b> ({fmt(df.loc[i_clean,'CO2'],1)} t CO₂/anno).</div>",
    unsafe_allow_html=True)

# ==========================================================================
# 9. MATRICE DECISIONALE A SEMAFORI
# ==========================================================================
st.markdown("## 🚦 Matrice di fattibilità")
st.markdown("<div class='h2-note'>Confronto per famiglia tecnologica. Ogni famiglia è "
            "rappresentata dalla sua variante più conveniente.</div>", unsafe_allow_html=True)

criteri = []

# 1. Autonomia sulla tratta
r = {"k": "Autonomia sulla tratta", "note": f"tratta richiesta {fmt(tratta)} km"}
for f in FAMS:
    q = rep[f]["Range"] / tratta if tratta else 99
    r[f] = (sem(q >= 1.25, q >= 1.0), f"{fmt(rep[f]['Range'])} km")
criteri.append(r)

# 2. Tempi di rifornimento
r = {"k": "Tempo di rifornimento", "note": "per singola sosta"}
for f in FAMS:
    h = rep[f]["StopH"]
    r[f] = (sem(h <= 0.35, h <= 1.0),
            f"{h*60:.0f} min" if h < 1 else f"{h:.1f} h")
criteri.append(r)

# 3. Carico utile
r = {"k": "Carico utile", "note": "perdita vs diesel, netto deroga UE"}
for f in FAMS:
    d = rep[f]["DPay"]
    quota = d / payload_nom if payload_nom else 0
    r[f] = (sem(quota <= 0.03, quota <= 0.10),
            "nessuna perdita" if d == 0 else f"−{fmt(d,2)} t")
criteri.append(r)

# 4. Costo
r = {"k": f"Costo totale ({UNIT_COSTO})", "note": f"anno {anno}, {scenario.lower()}"}
best = df[COSTO].min()
for f in FAMS:
    q = rep[f][COSTO] / best if best else 1
    r[f] = (sem(q <= 1.10, q <= 1.35), f"{fmt(rep[f][COSTO],3)}")
criteri.append(r)

# 5. Efficienza energetica
r = {"k": "Efficienza energetica", "note": "energia primaria per la stessa missione"}
best_p = df["Prim"].min()
for f in FAMS:
    q = rep[f]["Prim"] / best_p if best_p else 1
    r[f] = (sem(q <= 1.20, q <= 2.0), f"{fmt(rep[f]['Prim'])} MWh/anno")
criteri.append(r)

# 6. Vita della batteria
r = {"k": "Vita del sistema di accumulo", "note": f"{fmt(km_vita)} km nel ciclo di vita"}
for f in FAMS:
    n = rep[f]["NRepl"]
    r[f] = (sem(n == 0, n <= 1),
            "nessuna sostituzione" if n == 0 else f"{int(n)} sostituzion{'e' if n==1 else 'i'}")
criteri.append(r)

# 7. Infrastruttura
r = {"k": "Infrastruttura disponibile", "note": "sul territorio / al deposito"}
inf_map = {"ice": ("v", "rete capillare"),
           "bev": ({"Adeguata": "v", "Da potenziare": "g", "Insufficiente": "r"}[infra_el],
                   f"rete: {infra_el.lower()}"),
           "fcev": ({"Esistente": "v", "Pianificata": "g", "Assente": "r"}[infra_h2],
                    f"stazione H2: {infra_h2.lower()}")}
for f in FAMS:
    r[f] = inf_map[f]
criteri.append(r)

# 8. Emissioni
r = {"k": "Emissioni sul ciclo di vita", "note": "produzione + filiera + uso"}
best_c = df["CO2"].min()
for f in FAMS:
    q = rep[f]["CO2"] / best_c if best_c else 1
    r[f] = (sem(q <= 1.15, q <= 1.8), f"{fmt(rep[f]['CO2'],1)} t/anno")
criteri.append(r)

head = "".join(f"<th>{FAM_LBL[f]}</th>" for f in FAMS)
body = ""
for c in criteri:
    cells = "".join(f"<td>{badge(c[f][0])}<small>{c[f][1]}</small></td>" for f in FAMS)
    body += f"<tr><td class='k'>{c['k']}<small>{c['note']}</small></td>{cells}</tr>"
st.markdown(f"<table class='h2t'><thead><tr><th>Criterio</th>{head}</tr></thead>"
            f"<tbody>{body}</tbody></table>", unsafe_allow_html=True)

# ==========================================================================
# 10. VERDETTO PRATICO
# ==========================================================================
punti = {f: sum(1 for c in criteri if c[f][0] == "v") - sum(1 for c in criteri if c[f][0] == "r")
         for f in FAMS}
rossi = {f: [c["k"] for c in criteri if c[f][0] == "r"] for f in FAMS}
vince = max(punti, key=punti.get)

st.markdown("## 📌 Verdetto")
nome_v = FAM_LBL[vince]
if rossi[vince]:
    st.warning(f"**{nome_v}** ottiene il punteggio migliore ({punti[vince]:+d}), ma resta "
               f"critico su: {', '.join(rossi[vince]).lower()}. Va risolto prima di procedere.")
else:
    st.success(f"**{nome_v}** è la scelta più solida per questo profilo di utilizzo "
               f"(punteggio {punti[vince]:+d}, nessun criterio critico).")

cards = ""
for f in FAMS:
    r0 = rep[f]
    crit = rossi[f]
    stato = "nessun criterio critico" if not crit else "critico su: " + ", ".join(crit).lower()
    cards += (f"<div class='h2c' style='border-left-color:{FAM_COL[f]}'>"
              f"<div class='h2c-h'>{FAM_LBL[f]}</div>"
              f"<div class='h2c-s'>{r0['Nome']} · punteggio {punti[f]:+d} · {stato}</div>"
              f"<div class='h2c-r'><span>Costo</span><b>{fmt(r0[COSTO],3)} {UNIT_COSTO}</b></div>"
              f"<div class='h2c-r'><span>Autonomia reale</span><b>{fmt(r0['Range'])} km</b></div>"
              f"<div class='h2c-r'><span>Soste per tratta</span><b>{int(r0['StopsLeg'])}</b></div>"
              f"<div class='h2c-r'><span>Fermo annuo flotta</span><b>{fmt(r0['DownH'])} h</b></div>"
              f"<div class='h2c-r'><span>Energia comprata in viaggio</span>"
              f"<b>{r0['ShareRoad']*100:.0f}%</b></div>"
              f"<div class='h2c-r'><span>Emissioni</span><b>{fmt(r0['CO2'],1)} t/anno</b></div>"
              f"</div>")
st.markdown(f"<div class='h2-grid'>{cards}</div>", unsafe_allow_html=True)

# ==========================================================================
# 11. COMPOSIZIONE DEI COSTI
# ==========================================================================
def breakdown(segs, unit, dec=0):
    dd = df.sort_values("TCO", ascending=False)
    tot_max = dd[[s[0] for s in segs]].sum(axis=1).max() or 1
    out = "<div class='h2-leg'>" + "".join(
        f"<span><i style='background:{c}'></i>{l}</span>" for _, l, c in segs) + "</div>"
    for _, r0 in dd.iterrows():
        tot = sum(r0[s[0]] for s in segs)
        segs_html = ""
        for col, _, color in segs:
            if r0[col] <= 0:
                continue
            w = r0[col] / tot_max * 100
            txt = fmt(r0[col], dec) if (r0[col] / tot * 100 if tot else 0) > 12 else ""
            segs_html += f"<div class='h2b-seg' style='width:{w:.2f}%;background:{color}'>{txt}</div>"
        out += (f"<div class='h2b-row'><div class='h2b-label'>{r0['icon']} {r0['Nome']}</div>"
                f"<div class='h2b-track'>{segs_html}</div>"
                f"<div class='h2b-total'>{fmt(tot,dec)} <small>{unit}</small></div></div>")
    return out

with st.expander("📊 Da cosa derivano costi ed emissioni", expanded=False):
    st.markdown("**Composizione del costo annuo [€/anno]**")
    st.markdown(breakdown([("CAPEx", "Acquisto", "#0E6E7E"), ("Maint", "Manutenzione", "#C58A1A"),
                           ("Fuel", "Vettore energetico", "#A33B4A"),
                           ("Down", "Fermo per rifornimento", "#6B4E7D"),
                           ("Repl", "Sostituzione batteria", "#3E5C76")], "€/anno"),
                unsafe_allow_html=True)
    st.markdown("**Composizione delle emissioni [t CO₂/anno]**")
    st.markdown(breakdown([("WtT", "Filiera (WtT)", "#46586B"), ("TtW", "Scarico (TtW)", "#C2521E"),
                           ("Constr", "Produzione veicoli", "#8A94A0")], "t CO₂/anno", 1),
                unsafe_allow_html=True)

with st.expander("📋 Tabella dati completa", expanded=False):
    show = df.sort_values(COSTO).copy().reset_index(drop=True)
    show.insert(0, "#", show.index + 1)
    show["Consumo"] = show.apply(lambda r0: f"{r0['Consumo']:.3f} {CONS_LBL[r0['unit']]}", axis=1)
    cols = {"Nome": "Alimentazione", "Consumo": "Consumo", "Range": "Autonomia [km]",
            "PEff": "Prezzo eff.", "TCO": "Costo/anno [€]", "EurKm": "€/km",
            "EurTkm": "€/t·km", "CO2": "t CO₂/anno", "Prim": "MWh/anno",
            "PayEff": "Carico utile [t]", "NRepl": "Sost. batteria"}
    st.dataframe(show[["#"] + list(cols)].rename(columns=cols).style.format({
        "Autonomia [km]": "{:,.0f}", "Prezzo eff.": "{:,.2f}", "Costo/anno [€]": "€ {:,.0f}",
        "€/km": "{:.3f}", "€/t·km": "{:.3f}", "t CO₂/anno": "{:,.1f}",
        "MWh/anno": "{:,.0f}", "Carico utile [t]": "{:,.1f}"}), hide_index=True)
