import streamlit as st
import pandas as pd
import os

# ==========================================================================
# DSS COMUNI - Tool 2.4: Confronto sistemi di riscaldamento (H2 / Elc / FF)
# Standalone (nessun Excel) + multilingua (IT/EN/SL) + veste grafica H2READY.
# ==========================================================================

st.set_page_config(page_title="H2READY · Tool 2.4 Riscaldamento", page_icon="🔥", layout="wide")

# ==========================================================================
# 1. LINGUA
# ==========================================================================
LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

T = {
    "it": {
        "title": "🔥 Confronto sistemi di riscaldamento",
        "subtitle": "Quanto costa e quanto inquina ogni modo di riscaldare un edificio, a parità di calore prodotto.",
        "credits": "H2READY Toolkit · Tool 2.4 — sviluppato nel progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "case": "🎯 Il tuo caso",
        "prices": "💶 Prezzi dei vettori energetici",
        "fabbisogno": "Calore necessario all'anno [kWh]",
        "fabbisogno_help": "L'energia termica che serve per scaldare l'edificio in un anno. Una casa media sta intorno a 10.000 kWh.",
        "lifetime": "Durata dell'impianto [anni]",
        "lifetime_help": "Per quanti anni l'impianto resterà in funzione. Si usa per distribuire il costo d'acquisto e le emissioni di costruzione.",
        "cop": "Resa della pompa di calore (COP)",
        "cop_help": "Quante unità di calore produce la pompa per ogni unità di elettricità. 3 significa 3 volte più efficiente di una stufa elettrica.",
        "takeaway": "In questo scenario, la soluzione <b>più economica</b> è {cheap} (circa {cheap_v} €/anno) e quella <b>più pulita</b> è {clean} (circa {clean_v} kg CO₂/anno).",
        "sort_label": "Ordina le soluzioni per:",
        "sort_cost": "💶 Costo", "sort_co2": "🌱 Emissioni", "sort_eff": "⚡ Efficienza",
        "m_cost": "Costo annuo", "u_cost": "€/anno",
        "m_co2": "Emissioni", "u_co2": "kg CO₂/anno",
        "m_eff": "Efficienza (η / COP)",
        "m_prim": "Energia primaria", "u_prim": "kWh/anno",
        "badge_cheap": "💶 più economico", "badge_clean": "🌱 più pulito",
        "detail": "📊 Da cosa derivano costi ed emissioni",
        "chart_cost": "Composizione del costo annuo [€/anno]",
        "chart_em": "Composizione delle emissioni annue [kg CO₂/anno]",
        "leg_capex": "Acquisto (diviso per gli anni)", "leg_maint": "Manutenzione", "leg_fuel": "Vettore energetico",
        "leg_wtt": "Filiera (WtT)", "leg_ttw": "Camino (TtW)", "leg_constr": "Costruzione (divisa per gli anni)",
        "table": "📋 Tabella dati completa",
        "c_tech": "Soluzione", "c_prim": "Energia primaria", "c_eff": "η / COP", "c_em": "CO₂/anno", "c_cost": "Costo/anno",
        "note": "💡 La lunghezza delle barre indica la grandezza relativa; il <b>colore</b> dice se è un bene (verde) o un problema (rosso). Per costo, emissioni ed energia: più corto è meglio. Per l'efficienza: più lungo è meglio.",
        "names": {"boiler_oil": "Caldaia a gasolio", "boiler_gas": "Caldaia a metano", "stove_pellet": "Stufa a pellet",
                  "heat_pump": "Pompa di calore", "boiler_h2": "Caldaia a idrogeno"},
        "vectors": {"oil": "Gasolio", "ch4": "Metano", "pellet": "Pellet", "elc_grid": "Elettricità di rete",
                    "elc_self": "Autoproduzione", "h2_grey": "H₂ grigio", "h2_grid": "H₂ da rete", "h2_green": "H₂ verde"},
        "fuels": {"diesel": "Gasolio", "metano": "Metano", "pellet": "Pellet", "elc_rete": "Elettricità di rete",
                  "elc_auto": "Elettricità autoprodotta", "h2_grigio": "Idrogeno grigio", "h2_rete": "Idrogeno da rete",
                  "h2_verde_auto": "Idrogeno verde autoprodotto"},
    },
    "en": {
        "title": "🔥 Heating systems comparison",
        "subtitle": "How much each way of heating a building costs and pollutes, for the same amount of heat delivered.",
        "credits": "H2READY Toolkit · Tool 2.4 — developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "case": "🎯 Your case",
        "prices": "💶 Energy carrier prices",
        "fabbisogno": "Heat needed per year [kWh]",
        "fabbisogno_help": "The thermal energy needed to heat the building in one year. An average home is around 10,000 kWh.",
        "lifetime": "System lifetime [years]",
        "lifetime_help": "How many years the system will run. Used to spread the purchase cost and construction emissions.",
        "cop": "Heat pump performance (COP)",
        "cop_help": "How many units of heat the pump produces per unit of electricity. 3 means 3× more efficient than an electric heater.",
        "takeaway": "In this scenario, the <b>cheapest</b> option is {cheap} (about {cheap_v} €/yr) and the <b>cleanest</b> is {clean} (about {clean_v} kg CO₂/yr).",
        "sort_label": "Sort the options by:",
        "sort_cost": "💶 Cost", "sort_co2": "🌱 Emissions", "sort_eff": "⚡ Efficiency",
        "m_cost": "Annual cost", "u_cost": "€/yr",
        "m_co2": "Emissions", "u_co2": "kg CO₂/yr",
        "m_eff": "Efficiency (η / COP)",
        "m_prim": "Primary energy", "u_prim": "kWh/yr",
        "badge_cheap": "💶 cheapest", "badge_clean": "🌱 cleanest",
        "detail": "📊 Where costs and emissions come from",
        "chart_cost": "Annual cost breakdown [€/yr]",
        "chart_em": "Annual emissions breakdown [kg CO₂/yr]",
        "leg_capex": "Purchase (spread over years)", "leg_maint": "Maintenance", "leg_fuel": "Energy carrier",
        "leg_wtt": "Supply chain (WtT)", "leg_ttw": "Stack (TtW)", "leg_constr": "Construction (spread over years)",
        "table": "📋 Full data table",
        "c_tech": "Option", "c_prim": "Primary energy", "c_eff": "η / COP", "c_em": "CO₂/yr", "c_cost": "Cost/yr",
        "note": "💡 Bar length shows the relative size; the <b>colour</b> tells whether it's good (green) or a problem (red). For cost, emissions and energy: shorter is better. For efficiency: longer is better.",
        "names": {"boiler_oil": "Oil boiler", "boiler_gas": "Gas boiler", "stove_pellet": "Pellet stove",
                  "heat_pump": "Heat pump", "boiler_h2": "Hydrogen boiler"},
        "vectors": {"oil": "Oil", "ch4": "Gas", "pellet": "Pellet", "elc_grid": "Grid electricity",
                    "elc_self": "Self-produced", "h2_grey": "Grey H₂", "h2_grid": "Grid H₂", "h2_green": "Green H₂"},
        "fuels": {"diesel": "Oil", "metano": "Natural gas", "pellet": "Pellet", "elc_rete": "Grid electricity",
                  "elc_auto": "Self-produced electricity", "h2_grigio": "Grey hydrogen", "h2_rete": "Grid hydrogen",
                  "h2_verde_auto": "Self-produced green hydrogen"},
    },
    "sl": {
        "title": "🔥 Primerjava ogrevalnih sistemov",
        "subtitle": "Koliko stane in koliko onesnažuje vsak način ogrevanja stavbe ob enaki količini toplote.",
        "credits": "H2READY Toolkit · Orodje 2.4 — razvito v projektu [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready), avtor **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "case": "🎯 Vaš primer",
        "prices": "💶 Cene energentov",
        "fabbisogno": "Potrebna toplota na leto [kWh]",
        "fabbisogno_help": "Toplotna energija za ogrevanje stavbe v enem letu. Povprečna hiša znaša okoli 10.000 kWh.",
        "lifetime": "Življenjska doba sistema [leta]",
        "lifetime_help": "Koliko let bo sistem deloval. Uporablja se za porazdelitev nabavne cene in emisij izdelave.",
        "cop": "Učinkovitost toplotne črpalke (COP)",
        "cop_help": "Koliko enot toplote črpalka proizvede na enoto elektrike. 3 pomeni 3× bolj učinkovito od električnega grelnika.",
        "takeaway": "V tem scenariju je <b>najcenejša</b> rešitev {cheap} (približno {cheap_v} €/leto), <b>najčistejša</b> pa {clean} (približno {clean_v} kg CO₂/leto).",
        "sort_label": "Razvrsti rešitve po:",
        "sort_cost": "💶 Strošek", "sort_co2": "🌱 Emisije", "sort_eff": "⚡ Učinkovitost",
        "m_cost": "Letni strošek", "u_cost": "€/leto",
        "m_co2": "Emisije", "u_co2": "kg CO₂/leto",
        "m_eff": "Učinkovitost (η / COP)",
        "m_prim": "Primarna energija", "u_prim": "kWh/leto",
        "badge_cheap": "💶 najcenejše", "badge_clean": "🌱 najčistejše",
        "detail": "📊 Od kod izhajajo stroški in emisije",
        "chart_cost": "Sestava letnega stroška [€/leto]",
        "chart_em": "Sestava letnih emisij [kg CO₂/leto]",
        "leg_capex": "Nakup (porazdeljen na leta)", "leg_maint": "Vzdrževanje", "leg_fuel": "Energent",
        "leg_wtt": "Dobavna veriga (WtT)", "leg_ttw": "Dimnik (TtW)", "leg_constr": "Izdelava (porazdeljena na leta)",
        "table": "📋 Celotna tabela podatkov",
        "c_tech": "Rešitev", "c_prim": "Primarna energija", "c_eff": "η / COP", "c_em": "CO₂/leto", "c_cost": "Strošek/leto",
        "note": "💡 Dolžina stolpcev prikazuje relativno velikost; <b>barva</b> pove, ali je dobro (zeleno) ali težava (rdeče). Za strošek, emisije in energijo: krajše je bolje. Za učinkovitost: daljše je bolje.",
        "names": {"boiler_oil": "Oljni kotel", "boiler_gas": "Plinski kotel", "stove_pellet": "Peletna peč",
                  "heat_pump": "Toplotna črpalka", "boiler_h2": "Vodikov kotel"},
        "vectors": {"oil": "Olje", "ch4": "Plin", "pellet": "Pelet", "elc_grid": "Omrežna elektrika",
                    "elc_self": "Lastna proizvodnja", "h2_grey": "Sivi H₂", "h2_grid": "Omrežni H₂", "h2_green": "Zeleni H₂"},
        "fuels": {"diesel": "Olje", "metano": "Zemeljski plin", "pellet": "Pelet", "elc_rete": "Omrežna elektrika",
                  "elc_auto": "Lastna elektrika", "h2_grigio": "Sivi vodik", "h2_rete": "Omrežni vodik",
                  "h2_verde_auto": "Lastni zeleni vodik"},
    },
}
_t = T[LANG]

# ==========================================================================
# 2. DATI INCORPORATI (dal foglio CALORE - fabbisogno base 10.000 kWh/y)
# ==========================================================================
ICONS = {"boiler_oil": "🛢️", "boiler_gas": "🔥", "stove_pellet": "🪵", "heat_pump": "♨️", "boiler_h2": "💧"}

TECHNOLOGIES = [
    {"type": "boiler_oil",  "vector": "oil",      "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 12771.392082, "wtt_base": 444.305319,  "ttw_base": 2962.035457, "constr": 1200, "maint": 225.0,      "capex": 3500,  "fuel_key": "diesel",        "is_pdc": False},
    {"type": "boiler_gas",  "vector": "ch4",      "eta_cop": 1.0, "consumo_base": 10000.000000, "en_prim_base": 10989.010989, "wtt_base": 575.000000,  "ttw_base": 2050.000000, "constr": 950,  "maint": 200.0,      "capex": 2750,  "fuel_key": "metano",        "is_pdc": False},
    {"type": "stove_pellet","vector": "pellet",   "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 13071.895425, "wtt_base": 422.222222,  "ttw_base": 0.000000,    "constr": 650,  "maint": 300.0,      "capex": 3000,  "fuel_key": "pellet",        "is_pdc": False},
    {"type": "heat_pump",   "vector": "elc_grid", "eta_cop": 3.0, "consumo_base": 3333.333333,  "en_prim_base": 6666.666667,  "wtt_base": 716.666667,  "ttw_base": 0.000000,    "constr": 1400, "maint": 150.0,      "capex": 11500, "fuel_key": "elc_rete",      "is_pdc": True},
    {"type": "heat_pump",   "vector": "elc_self", "eta_cop": 3.0, "consumo_base": 3333.333333,  "en_prim_base": 3703.703704,  "wtt_base": 183.333333,  "ttw_base": 0.000000,    "constr": 1400, "maint": 150.0,      "capex": 11500, "fuel_key": "elc_auto",      "is_pdc": True},
    {"type": "boiler_h2",   "vector": "h2_grey",  "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 15873.015873, "wtt_base": 3667.033370, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909, "capex": 7000,  "fuel_key": "h2_grigio",     "is_pdc": False},
    {"type": "boiler_h2",   "vector": "h2_grid",  "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 40404.040404, "wtt_base": 4300.430043, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909, "capex": 7000,  "fuel_key": "h2_rete",       "is_pdc": False},
    {"type": "boiler_h2",   "vector": "h2_green", "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 17921.146953, "wtt_base": 1000.100010, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909, "capex": 7000,  "fuel_key": "h2_verde_auto", "is_pdc": False},
]

FUELS = {
    "diesel":        {"natura": 1.8,  "factor": 0.10097848148559},
    "metano":        {"natura": 0.95, "factor": 0.10427528675703},
    "pellet":        {"natura": 4.5,  "factor": 0.01360544217687},
    "elc_rete":      {"natura": 0.31, "factor": 1.0},
    "elc_auto":      {"natura": 0.24, "factor": 1.0},
    "h2_grigio":     {"natura": 2.0,  "factor": 0.03000300030003},
    "h2_rete":       {"natura": 20.0, "factor": 0.03000300030003},
    "h2_verde_auto": {"natura": 15.0, "factor": 0.03000300030003},
}
FUEL_UNITS = {"diesel": {"it": "€/l", "en": "€/l", "sl": "€/l"},
              "metano": {"it": "€/Sm³", "en": "€/Sm³", "sl": "€/Sm³"},
              "pellet": {"it": "€/sacco", "en": "€/bag", "sl": "€/vreča"},
              "elc_rete": {"it": "€/kWh", "en": "€/kWh", "sl": "€/kWh"},
              "elc_auto": {"it": "€/kWh", "en": "€/kWh", "sl": "€/kWh"},
              "h2_grigio": {"it": "€/kg", "en": "€/kg", "sl": "€/kg"},
              "h2_rete": {"it": "€/kg", "en": "€/kg", "sl": "€/kg"},
              "h2_verde_auto": {"it": "€/kg", "en": "€/kg", "sl": "€/kg"}}

DEFAULT_FABBISOGNO, DEFAULT_LIFETIME, DEFAULT_COP = 10000, 20, 3.0

# ==========================================================================
# 3. STILE (coerente con gli altri tool H2READY)
# ==========================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap');
/* I testi NON impostano un colore: ereditano quello del tema Streamlit
   (scuro su tema chiaro, chiaro su tema scuro). I "tenui" usano l'opacità. */
.h4-sub { opacity:.7; font-size:0.96rem; margin:-4px 0 2px 0; }
.h4-take { display:flex; flex-wrap:wrap; gap:14px; background:rgba(13,124,92,.13);
           border:1px solid rgba(13,124,92,.40); border-left:6px solid #0D7C5C; border-radius:12px;
           padding:14px 18px; margin:14px 0 6px 0; font-size:0.98rem; }
.h4-note { opacity:.6; font-size:0.8rem; margin:10px 0 2px 0; }
.h4-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:14px; margin-top:8px; }
.h4c { background:rgba(127,127,127,.10); border:1px solid rgba(127,127,127,.26);
       border-left-width:6px; border-radius:13px; padding:15px 17px 14px 17px; box-shadow:0 1px 2px rgba(0,0,0,.10); }
.h4c-top { display:flex; align-items:flex-start; justify-content:space-between; gap:10px; margin-bottom:12px; }
.h4c-name { font-weight:700; font-size:1.04rem; line-height:1.2; }
.h4c-name .ic { margin-right:6px; }
.h4c-tags { display:flex; flex-direction:column; align-items:flex-end; gap:4px; flex:0 0 auto; }
.h4c-vchip { font-size:.7rem; background:rgba(127,127,127,.16); border:1px solid rgba(127,127,127,.30);
             border-radius:6px; padding:2px 8px; white-space:nowrap; opacity:.92; }
.h4c-badge { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.66rem; letter-spacing:.04em; text-transform:uppercase;
             color:#fff; padding:3px 8px; border-radius:6px; white-space:nowrap; }
.h4c-metrics { display:grid; grid-template-columns:1fr 1fr; gap:11px 16px; }
.h4m-head { display:flex; justify-content:space-between; align-items:baseline; gap:6px; margin-bottom:4px; }
.h4m-lbl { font-size:.72rem; opacity:.6; text-transform:uppercase; letter-spacing:.03em; }
.h4m-val { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.0rem; }
.h4m-bar { height:7px; border-radius:5px; background:rgba(127,127,127,.20); overflow:hidden; }
.h4m-fill { height:100%; border-radius:5px; }
@media (max-width:560px){ .h4c-metrics{ grid-template-columns:1fr; } }
.h4-bd-title { font-weight:700; font-size:0.98rem; margin:16px 0 8px 0; }
.h4-leg { display:flex; flex-wrap:wrap; gap:14px; margin-bottom:12px; }
.h4-leg span { display:flex; align-items:center; gap:6px; font-size:.78rem; opacity:.85; }
.h4-leg i { width:12px; height:12px; border-radius:3px; display:inline-block; }
.h4b-row { display:grid; grid-template-columns:215px 1fr 118px; align-items:center; gap:12px; margin-bottom:9px; }
.h4b-label { font-size:.83rem; font-weight:600; text-align:right; line-height:1.2; }
.h4b-track { display:flex; height:24px; border-radius:6px; overflow:hidden;
             background:rgba(127,127,127,.18); border:1px solid rgba(127,127,127,.28); }
.h4b-seg { height:100%; display:flex; align-items:center; justify-content:center; color:#fff;
           font-size:.69rem; font-weight:700; font-family:'Space Grotesk',sans-serif; white-space:nowrap; overflow:hidden;
           text-shadow:0 1px 1px rgba(0,0,0,.45); }
.h4b-total { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.95rem; }
.h4b-total small { opacity:.55; font-weight:500; font-size:.66rem; }
@media (max-width:560px){ .h4b-row{ grid-template-columns:120px 1fr 84px; } }
</style>
"""

# ==========================================================================
# 4. SIDEBAR - PARAMETRI
# ==========================================================================
st.sidebar.markdown(f"### {_t['case']}")
user_fabbisogno = st.sidebar.slider(_t["fabbisogno"], 2000, 50000, DEFAULT_FABBISOGNO, 1000, help=_t["fabbisogno_help"])
user_lifetime = st.sidebar.slider(_t["lifetime"], 1, 30, DEFAULT_LIFETIME, 1, help=_t["lifetime_help"])
user_cop = st.sidebar.number_input(_t["cop"], value=DEFAULT_COP, step=0.1, help=_t["cop_help"])

prezzi_kwh = {}
with st.sidebar.expander(_t["prices"], expanded=False):
    for key, f in FUELS.items():
        unit = FUEL_UNITS[key][LANG]
        user_val = st.number_input(f"{_t['fuels'][key]} [{unit}]", value=float(f["natura"]), format="%.3f", key=f"fuel_{key}")
        prezzi_kwh[key] = user_val * f["factor"]

# ==========================================================================
# 5. MOTORE DI CALCOLO
# ==========================================================================
def calcola(t):
    eta = user_cop if t["is_pdc"] else t["eta_cop"]
    if eta == 0:
        eta = 1.0
    consumo_vettore = user_fabbisogno / eta
    cb = t["consumo_base"] if t["consumo_base"] > 0 else 1.0
    scala = consumo_vettore / cb
    wtt = consumo_vettore * (t["wtt_base"] / cb)
    ttw = consumo_vettore * (t["ttw_base"] / cb)
    costruz = t["constr"] / user_lifetime
    fuel = consumo_vettore * prezzi_kwh.get(t["fuel_key"], 0.10)
    capex = t["capex"] / user_lifetime
    return {
        "type": t["type"], "vector": t["vector"], "icon": ICONS[t["type"]],
        "Nome": _t["names"][t["type"]], "Vettore": _t["vectors"][t["vector"]],
        "En_Primaria": t["en_prim_base"] * scala, "Eta": eta,
        "WtT": wtt, "TtW": ttw, "Costruz": costruz, "Emiss": wtt + ttw + costruz,
        "Fuel": fuel, "Maint": t["maint"], "CAPEx": capex, "Costo": fuel + t["maint"] + capex,
    }

df = pd.DataFrame([calcola(t) for t in TECHNOLOGIES])

# ==========================================================================
# 6. COLORI (scala verde->ambra->rosso) E HELPER
# ==========================================================================
def lerp(frac):
    frac = max(0.0, min(1.0, frac))
    stops = [(13, 124, 92), (28, 124, 140), (201, 138, 27), (212, 98, 43), (163, 59, 74)]
    pos = frac * (len(stops) - 1)
    i = int(pos)
    if i >= len(stops) - 1:
        r, g, b = stops[-1]
    else:
        f = pos - i
        a, c = stops[i], stops[i + 1]
        r, g, b = (round(a[j] + (c[j] - a[j]) * f) for j in range(3))
    return f"#{r:02X}{g:02X}{b:02X}"

def frac_of(series, val, higher_is_better=False):
    lo, hi = series.min(), series.max()
    f = 0.0 if hi == lo else (val - lo) / (hi - lo)
    return (1 - f) if higher_is_better else f

def fmt(v):
    return f"{v:,.0f}".replace(",", ".")

idx_cheap = df["Costo"].idxmin()
idx_clean = df["Emiss"].idxmin()

# ==========================================================================
# 7. INTESTAZIONE + MESSAGGIO CHIAVE
# ==========================================================================
st.markdown(CSS, unsafe_allow_html=True)
st.title(_t["title"])
st.markdown(f"<div class='h4-sub'>{_t['subtitle']}</div>", unsafe_allow_html=True)
st.caption(_t["credits"])

if os.path.exists("ReadMe_calore.md"):
    with st.expander("ℹ️"):
        with open("ReadMe_calore.md", "r", encoding="utf-8") as fh:
            st.markdown(fh.read())

take = _t["takeaway"].format(
    cheap=df.loc[idx_cheap, "Nome"] + " · " + df.loc[idx_cheap, "Vettore"], cheap_v=fmt(df.loc[idx_cheap, "Costo"]),
    clean=df.loc[idx_clean, "Nome"] + " · " + df.loc[idx_clean, "Vettore"], clean_v=fmt(df.loc[idx_clean, "Emiss"]),
)
st.markdown(f"<div class='h4-take'>{take}</div>", unsafe_allow_html=True)

# ==========================================================================
# 8. CONTROLLO ORDINAMENTO + SCHEDE
# ==========================================================================
sort_map = {_t["sort_cost"]: ("Costo", False), _t["sort_co2"]: ("Emiss", False), _t["sort_eff"]: ("Eta", True)}
sort_choice = st.radio(_t["sort_label"], list(sort_map.keys()), horizontal=True)
sort_col, sort_desc = sort_map[sort_choice]
df_sorted = df.sort_values(sort_col, ascending=not sort_desc)

st.markdown(f"<div class='h4-note'>{_t['note']}</div>", unsafe_allow_html=True)

def metric_block(label, value, unit, frac, fill_ratio):
    color = lerp(frac)
    w = max(3, min(100, fill_ratio * 100))
    unit_html = f"<span style='font-size:.62rem;color:#9AA6B2;font-weight:500'> {unit}</span>" if unit else ""
    return (
        f"<div><div class='h4m-head'><span class='h4m-lbl'>{label}</span>"
        f"<span class='h4m-val' style='color:{color}'>{value}{unit_html}</span></div>"
        f"<div class='h4m-bar'><div class='h4m-fill' style='width:{w:.0f}%;background:{color}'></div></div></div>"
    )

cards = ""
for i, r in df_sorted.iterrows():
    accent = lerp(frac_of(df["Emiss"], r["Emiss"]))
    badges = ""
    if i == idx_cheap:
        badges += f"<span class='h4c-badge' style='background:#1C7C8C'>{_t['badge_cheap']}</span>"
    if i == idx_clean:
        badges += f"<span class='h4c-badge' style='background:#0B6E4F'>{_t['badge_clean']}</span>"

    m_cost = metric_block(_t["m_cost"], fmt(r["Costo"]), _t["u_cost"],
                          frac_of(df["Costo"], r["Costo"]), r["Costo"] / df["Costo"].max())
    m_co2 = metric_block(_t["m_co2"], fmt(r["Emiss"]), _t["u_co2"],
                         frac_of(df["Emiss"], r["Emiss"]), r["Emiss"] / df["Emiss"].max())
    m_eff = metric_block(_t["m_eff"], f"{r['Eta']:.1f}".replace(".", ","), "",
                         frac_of(df["Eta"], r["Eta"], higher_is_better=True), r["Eta"] / df["Eta"].max())
    m_prim = metric_block(_t["m_prim"], fmt(r["En_Primaria"]), _t["u_prim"],
                          frac_of(df["En_Primaria"], r["En_Primaria"]), r["En_Primaria"] / df["En_Primaria"].max())

    cards += (
        f"<div class='h4c' style='border-left-color:{accent}'>"
        f"<div class='h4c-top'><div class='h4c-name'><span class='ic'>{r['icon']}</span>{r['Nome']}</div>"
        f"<div class='h4c-tags'>{badges}<span class='h4c-vchip'>{r['Vettore']}</span></div></div>"
        f"<div class='h4c-metrics'>{m_cost}{m_co2}{m_eff}{m_prim}</div></div>"
    )

st.markdown(f"<div class='h4-grid'>{cards}</div>", unsafe_allow_html=True)

# ==========================================================================
# 9. DETTAGLIO COMPOSIZIONE (barre impilate HTML ad alto contrasto)
# ==========================================================================
df["Label"] = df["Nome"] + " · " + df["Vettore"]

def render_breakdown(data, segments, unit, sort_col):
    """data: DataFrame; segments: list of (col, label, color); unit: str."""
    dd = data.sort_values(sort_col, ascending=False)
    totals = dd[[s[0] for s in segments]].sum(axis=1)
    max_total = totals.max() if totals.max() > 0 else 1.0

    legend = "<div class='h4-leg'>" + "".join(
        f"<span><i style='background:{c}'></i>{lbl}</span>" for _, lbl, c in segments) + "</div>"

    rows = ""
    for idx, r in dd.iterrows():
        total = sum(r[s[0]] for s in segments)
        segs = ""
        for col, lbl, color in segments:
            val = r[col]
            if val <= 0:
                continue
            w_track = val / max_total * 100          # larghezza rispetto al massimo
            w_in = val / total * 100 if total > 0 else 0  # quota dentro la barra
            txt = fmt(val) if w_in > 11 else ""
            segs += f"<div class='h4b-seg' style='width:{w_track:.2f}%;background:{color}'>{txt}</div>"
        rows += (
            f"<div class='h4b-row'>"
            f"<div class='h4b-label'>{r['icon']} {r['Label']}</div>"
            f"<div class='h4b-track'>{segs}</div>"
            f"<div class='h4b-total'>{fmt(total)} <small>{unit}</small></div>"
            f"</div>"
        )
    return legend + rows

with st.expander(_t["detail"], expanded=True):
    st.markdown(f"<div class='h4-bd-title'>{_t['chart_cost']}</div>", unsafe_allow_html=True)
    cost_segments = [("CAPEx", _t["leg_capex"], "#0E6E7E"), ("Maint", _t["leg_maint"], "#C58A1A"), ("Fuel", _t["leg_fuel"], "#A33B4A")]
    st.markdown(render_breakdown(df, cost_segments, _t["u_cost"], "Costo"), unsafe_allow_html=True)

    st.markdown(f"<div class='h4-bd-title'>{_t['chart_em']}</div>", unsafe_allow_html=True)
    em_segments = [("WtT", _t["leg_wtt"], "#46586B"), ("TtW", _t["leg_ttw"], "#C2521E"), ("Costruz", _t["leg_constr"], "#8A94A0")]
    st.markdown(render_breakdown(df, em_segments, _t["u_co2"], "Emiss"), unsafe_allow_html=True)

# ==========================================================================
# 10. TABELLA DATI
# ==========================================================================
with st.expander(_t["table"]):
    show = df.sort_values("Costo")[["Label", "En_Primaria", "Eta", "Emiss", "Costo"]].rename(columns={
        "Label": _t["c_tech"], "En_Primaria": _t["c_prim"], "Eta": _t["c_eff"], "Emiss": _t["c_em"], "Costo": _t["c_cost"]})
    st.dataframe(show.style.format({_t["c_prim"]: "{:,.0f}", _t["c_eff"]: "{:.2f}",
                                    _t["c_em"]: "{:,.0f}", _t["c_cost"]: "€ {:,.0f}"}), use_container_width=True)
