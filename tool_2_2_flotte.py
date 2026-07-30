import streamlit as st
import pandas as pd
import re

# ==========================================================================
# H2READY TOOLKIT - Tool 2.2: TCO & confronto flotte
# Diesel / Benzina vs Elettrico (BEV) vs Idrogeno (FCEV)
#
# Versione STANDALONE + multilingua (IT/EN/SL) + veste grafica H2READY.
# I dati tecnico-economici sono INCORPORATI nel codice e derivano dai fogli
# AUTO / CAMION / AUTOBUS Urbano / AUTOBUS ExtraUrbano del file
# "Comparison H2 elc FF.xlsx" (medie dei modelli di mercato censiti).
#
# NOTA: per l'autobus urbano elettrico il foglio riportava in una colonna
# 2,3 kWh/km (valore del singolo Mercedes eCitaro) mentre tutti i calcoli di
# costo ed emissioni usavano la media dei modelli (1,6775 kWh/km): qui si usa
# il valore coerente con i calcoli, cioè la media.
# ==========================================================================

st.set_page_config(page_title="H2READY · Tool 2.2 Flotte", page_icon="🚚", layout="wide")

# ==========================================================================
# 1. LINGUA
# ==========================================================================
LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

T = {
    "it": {
        "title": "🚚 Confronto flotte e costo totale (TCO)",
        "subtitle": "Quanto costa e quanto inquina ogni alimentazione, a parità di chilometri percorsi.",
        "credits": "H2READY Toolkit · Tool 2.2 — sviluppato nel progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "case": "🎯 La tua flotta",
        "vehicle": "Tipo di veicolo",
        "vehicle_help": "Scegli la categoria: i consumi, i costi d'acquisto e la manutenzione cambiano molto tra un'auto e un camion.",
        "fleet": "Numero di veicoli",
        "fleet_help": "Quanti mezzi di questo tipo compongono la flotta da confrontare.",
        "km": "Chilometri all'anno per veicolo",
        "km_help": "Percorrenza media annua di un singolo mezzo. È il parametro che pesa di più sul risultato.",
        "life": "Durata del veicolo [anni]",
        "life_help": "Anni di servizio previsti. Serve a distribuire il costo d'acquisto e le emissioni di produzione del veicolo.",
        "prices": "💶 Prezzi dei vettori energetici",
        "takeaway": "Per {n} {veh} che percorrono {km} km/anno ciascuno, la soluzione **più economica** è {cheap} (circa {cheap_v} €/anno in totale) e quella **più pulita** è {clean} (circa {clean_v} t CO₂/anno).",
        "sort_label": "Ordina per:",
        "sort_cost": "💶 Costo totale", "sort_co2": "🌱 Emissioni", "sort_km": "📏 Costo per km",
        "m_tco": "Costo totale annuo", "u_tco": "€/anno",
        "m_co2": "Emissioni", "u_co2": "t CO₂/anno",
        "m_km": "Costo per km", "u_km": "€/km",
        "m_prim": "Energia primaria", "u_prim": "MWh/anno",
        "badge_cheap": "💶 più economico", "badge_clean": "🌱 più pulito",
        "note": "💡 La lunghezza delle barre indica la grandezza relativa; il <b>colore</b> dice se è un bene (verde) o un problema (rosso). Per costi, emissioni ed energia: più corto è meglio.",
        "detail": "📊 Da cosa derivano costi ed emissioni",
        "chart_cost": "Composizione del costo annuo della flotta [€/anno]",
        "chart_em": "Composizione delle emissioni annue [t CO₂/anno]",
        "leg_capex": "Acquisto (diviso per gli anni)", "leg_maint": "Manutenzione", "leg_fuel": "Vettore energetico",
        "leg_wtt": "Filiera (WtT)", "leg_ttw": "Scarico (TtW)", "leg_constr": "Produzione veicoli (divisa per gli anni)",
        "table": "📋 Tabella dati completa",
        "c_vec": "Alimentazione", "c_cons": "Consumo", "c_tco": "Costo/anno", "c_km": "€/km", "c_co2": "t CO₂/anno", "c_prim": "MWh/anno",
        "fleet_recap": "Flotta: {n} × {veh} · {tot} km/anno complessivi",
        "vehicles": {"auto": "Auto / veicoli leggeri", "truck": "Camion pesanti", "bus_u": "Autobus urbano", "bus_x": "Autobus extraurbano"},
        "vectors": {"benzina": "Benzina", "diesel": "Diesel", "elc_rete": "Elettrico (rete)", "elc_auto": "Elettrico (autoprodotto)",
                    "h2_grigio": "Idrogeno grigio", "h2_rete": "Idrogeno da rete", "h2_verde": "Idrogeno verde autoprodotto"},
        "fuels": {"benzina": "Benzina", "diesel": "Diesel", "elc_rete": "Elettricità di rete", "elc_auto": "Elettricità autoprodotta",
                  "h2_grigio": "Idrogeno grigio", "h2_rete": "Idrogeno da rete", "h2_verde": "Idrogeno verde autoprodotto"},
        "units": {"benzina": "€/l", "diesel": "€/l", "elc_rete": "€/kWh", "elc_auto": "€/kWh",
                  "h2_grigio": "€/kg", "h2_rete": "€/kg", "h2_verde": "€/kg"},
        "cons_units": {"l": "l/km", "kwh": "kWh/km", "kg": "kg/km"},
    },
    "en": {
        "title": "🚚 Fleet comparison and total cost (TCO)",
        "subtitle": "How much each fuel option costs and pollutes, for the same distance driven.",
        "credits": "H2READY Toolkit · Tool 2.2 — developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "case": "🎯 Your fleet",
        "vehicle": "Vehicle type",
        "vehicle_help": "Pick the category: consumption, purchase cost and maintenance differ widely between a car and a truck.",
        "fleet": "Number of vehicles",
        "fleet_help": "How many vehicles of this type make up the fleet being compared.",
        "km": "Kilometres per year per vehicle",
        "km_help": "Average annual distance of a single vehicle. This is the parameter with the largest impact on results.",
        "life": "Vehicle lifetime [years]",
        "life_help": "Expected years of service. Used to spread the purchase cost and the vehicle manufacturing emissions.",
        "prices": "💶 Energy carrier prices",
        "takeaway": "For {n} {veh} driving {km} km/year each, the **cheapest** option is {cheap} (about {cheap_v} €/yr in total) and the **cleanest** is {clean} (about {clean_v} t CO₂/yr).",
        "sort_label": "Sort by:",
        "sort_cost": "💶 Total cost", "sort_co2": "🌱 Emissions", "sort_km": "📏 Cost per km",
        "m_tco": "Total annual cost", "u_tco": "€/yr",
        "m_co2": "Emissions", "u_co2": "t CO₂/yr",
        "m_km": "Cost per km", "u_km": "€/km",
        "m_prim": "Primary energy", "u_prim": "MWh/yr",
        "badge_cheap": "💶 cheapest", "badge_clean": "🌱 cleanest",
        "note": "💡 Bar length shows the relative size; the <b>colour</b> tells whether it's good (green) or a problem (red). For costs, emissions and energy: shorter is better.",
        "detail": "📊 Where costs and emissions come from",
        "chart_cost": "Annual fleet cost breakdown [€/yr]",
        "chart_em": "Annual emissions breakdown [t CO₂/yr]",
        "leg_capex": "Purchase (spread over years)", "leg_maint": "Maintenance", "leg_fuel": "Energy carrier",
        "leg_wtt": "Supply chain (WtT)", "leg_ttw": "Tailpipe (TtW)", "leg_constr": "Vehicle manufacturing (spread over years)",
        "table": "📋 Full data table",
        "c_vec": "Powertrain", "c_cons": "Consumption", "c_tco": "Cost/yr", "c_km": "€/km", "c_co2": "t CO₂/yr", "c_prim": "MWh/yr",
        "fleet_recap": "Fleet: {n} × {veh} · {tot} km/year in total",
        "vehicles": {"auto": "Cars / light vehicles", "truck": "Heavy trucks", "bus_u": "Urban bus", "bus_x": "Intercity bus"},
        "vectors": {"benzina": "Petrol", "diesel": "Diesel", "elc_rete": "Electric (grid)", "elc_auto": "Electric (self-produced)",
                    "h2_grigio": "Grey hydrogen", "h2_rete": "Grid hydrogen", "h2_verde": "Self-produced green hydrogen"},
        "fuels": {"benzina": "Petrol", "diesel": "Diesel", "elc_rete": "Grid electricity", "elc_auto": "Self-produced electricity",
                  "h2_grigio": "Grey hydrogen", "h2_rete": "Grid hydrogen", "h2_verde": "Self-produced green hydrogen"},
        "units": {"benzina": "€/l", "diesel": "€/l", "elc_rete": "€/kWh", "elc_auto": "€/kWh",
                  "h2_grigio": "€/kg", "h2_rete": "€/kg", "h2_verde": "€/kg"},
        "cons_units": {"l": "l/km", "kwh": "kWh/km", "kg": "kg/km"},
    },
    "sl": {
        "title": "🚚 Primerjava voznih parkov in skupni stroški (TCO)",
        "subtitle": "Koliko stane in koliko onesnažuje vsak pogon ob enaki prevoženi razdalji.",
        "credits": "H2READY Toolkit · Orodje 2.2 — razvito v projektu [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready), avtor **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "case": "🎯 Vaš vozni park",
        "vehicle": "Vrsta vozila",
        "vehicle_help": "Izberite kategorijo: poraba, nabavna cena in vzdrževanje se med avtomobilom in tovornjakom močno razlikujejo.",
        "fleet": "Število vozil",
        "fleet_help": "Koliko vozil te vrste sestavlja vozni park, ki ga primerjate.",
        "km": "Kilometrov na leto na vozilo",
        "km_help": "Povprečna letna razdalja posameznega vozila. Ta parameter najbolj vpliva na rezultat.",
        "life": "Življenjska doba vozila [leta]",
        "life_help": "Predvidena leta uporabe. Uporablja se za porazdelitev nabavne cene in emisij izdelave vozila.",
        "prices": "💶 Cene energentov",
        "takeaway": "Za {n} {veh}, ki prevozijo {km} km/leto vsako, je **najcenejša** rešitev {cheap} (skupaj približno {cheap_v} €/leto), **najčistejša** pa {clean} (približno {clean_v} t CO₂/leto).",
        "sort_label": "Razvrsti po:",
        "sort_cost": "💶 Skupni strošek", "sort_co2": "🌱 Emisije", "sort_km": "📏 Strošek na km",
        "m_tco": "Skupni letni strošek", "u_tco": "€/leto",
        "m_co2": "Emisije", "u_co2": "t CO₂/leto",
        "m_km": "Strošek na km", "u_km": "€/km",
        "m_prim": "Primarna energija", "u_prim": "MWh/leto",
        "badge_cheap": "💶 najcenejše", "badge_clean": "🌱 najčistejše",
        "note": "💡 Dolžina stolpcev prikazuje relativno velikost; <b>barva</b> pove, ali je dobro (zeleno) ali težava (rdeče). Za stroške, emisije in energijo: krajše je bolje.",
        "detail": "📊 Od kod izhajajo stroški in emisije",
        "chart_cost": "Sestava letnega stroška voznega parka [€/leto]",
        "chart_em": "Sestava letnih emisij [t CO₂/leto]",
        "leg_capex": "Nakup (porazdeljen na leta)", "leg_maint": "Vzdrževanje", "leg_fuel": "Energent",
        "leg_wtt": "Dobavna veriga (WtT)", "leg_ttw": "Izpuh (TtW)", "leg_constr": "Izdelava vozil (porazdeljena na leta)",
        "table": "📋 Celotna tabela podatkov",
        "c_vec": "Pogon", "c_cons": "Poraba", "c_tco": "Strošek/leto", "c_km": "€/km", "c_co2": "t CO₂/leto", "c_prim": "MWh/leto",
        "fleet_recap": "Vozni park: {n} × {veh} · skupaj {tot} km/leto",
        "vehicles": {"auto": "Avtomobili / lahka vozila", "truck": "Težki tovornjaki", "bus_u": "Mestni avtobus", "bus_x": "Medkrajevni avtobus"},
        "vectors": {"benzina": "Bencin", "diesel": "Dizel", "elc_rete": "Električni (omrežje)", "elc_auto": "Električni (lastna proizvodnja)",
                    "h2_grigio": "Sivi vodik", "h2_rete": "Omrežni vodik", "h2_verde": "Lastni zeleni vodik"},
        "fuels": {"benzina": "Bencin", "diesel": "Dizel", "elc_rete": "Omrežna elektrika", "elc_auto": "Lastna elektrika",
                  "h2_grigio": "Sivi vodik", "h2_rete": "Omrežni vodik", "h2_verde": "Lastni zeleni vodik"},
        "units": {"benzina": "€/l", "diesel": "€/l", "elc_rete": "€/kWh", "elc_auto": "€/kWh",
                  "h2_grigio": "€/kg", "h2_rete": "€/kg", "h2_verde": "€/kg"},
        "cons_units": {"l": "l/km", "kwh": "kWh/km", "kg": "kg/km"},
    },
}
_t = T[LANG]

# ==========================================================================
# 2. DATI INCORPORATI (per km e per veicolo)
#    cons     = consumo in unità naturali per km (l/km, kWh/km, kg/km)
#    prim     = energia primaria [kWh/km]
#    wtt/ttw  = emissioni [kg CO2/km]
#    constr   = emissioni di produzione del veicolo [kg CO2, totale]
#    maint    = manutenzione [€/km]
#    capex    = costo d'acquisto del veicolo [€]
# ==========================================================================
VEHICLES = {
    "auto":  {"icon": "🚗", "life": 20, "km_default": 15000,  "km_max": 60000,
              "vectors": {
                  "benzina":   {"unit": "l",   "cons": 0.067250, "prim": 0.6925, "wtt": 0.03884, "ttw": 0.15535, "constr": 6000,  "maint": 0.0800, "capex": 41000},
                  "diesel":    {"unit": "l",   "cons": 0.054000, "prim": 0.6147, "wtt": 0.02138, "ttw": 0.14256, "constr": 6000,  "maint": 0.0650, "capex": 45000},
                  "elc_rete":  {"unit": "kwh", "cons": 0.136667, "prim": 0.2733, "wtt": 0.02938, "ttw": 0.0,     "constr": 12000, "maint": 0.0300, "capex": 38333},
                  "elc_auto":  {"unit": "kwh", "cons": 0.136667, "prim": 0.1519, "wtt": 0.00752, "ttw": 0.0,     "constr": 12000, "maint": 0.0300, "capex": 38333},
                  "h2_grigio": {"unit": "kg",  "cons": 0.010000, "prim": 0.4761, "wtt": 0.11000, "ttw": 0.0,     "constr": 14000, "maint": 0.0550, "capex": 67500},
                  "h2_rete":   {"unit": "kg",  "cons": 0.010000, "prim": 1.2120, "wtt": 0.12900, "ttw": 0.0,     "constr": 14000, "maint": 0.0550, "capex": 67500},
                  "h2_verde":  {"unit": "kg",  "cons": 0.010000, "prim": 0.5376, "wtt": 0.03000, "ttw": 0.0,     "constr": 14000, "maint": 0.0550, "capex": 67500},
              }},
    "truck": {"icon": "🚛", "life": 7, "km_default": 170000, "km_max": 300000,
              "vectors": {
                  "diesel":    {"unit": "l",   "cons": 0.330000, "prim": 3.7563,  "wtt": 0.13068, "ttw": 0.87120, "constr": 60000,  "maint": 0.2500, "capex": 115000},
                  "elc_rete":  {"unit": "kwh", "cons": 1.572500, "prim": 3.1450,  "wtt": 0.33809, "ttw": 0.0,     "constr": 110000, "maint": 0.1400, "capex": 245000},
                  "elc_auto":  {"unit": "kwh", "cons": 1.572500, "prim": 1.7472,  "wtt": 0.08649, "ttw": 0.0,     "constr": 110000, "maint": 0.1400, "capex": 245000},
                  "h2_grigio": {"unit": "kg",  "cons": 0.084167, "prim": 4.0075,  "wtt": 0.92583, "ttw": 0.0,     "constr": 125000, "maint": 0.2000, "capex": 400000},
                  "h2_rete":   {"unit": "kg",  "cons": 0.084167, "prim": 10.2010, "wtt": 1.08575, "ttw": 0.0,     "constr": 125000, "maint": 0.2000, "capex": 400000},
                  "h2_verde":  {"unit": "kg",  "cons": 0.084167, "prim": 4.5246,  "wtt": 0.25250, "ttw": 0.0,     "constr": 125000, "maint": 0.2000, "capex": 400000},
              }},
    "bus_u": {"icon": "🚌", "life": 13, "km_default": 70000, "km_max": 150000,
              "vectors": {
                  "diesel":    {"unit": "l",   "cons": 0.386667, "prim": 4.4014,  "wtt": 0.15312, "ttw": 1.02080, "constr": 50000, "maint": 0.3250, "capex": 213333},
                  "elc_rete":  {"unit": "kwh", "cons": 1.677500, "prim": 3.3550,  "wtt": 0.36066, "ttw": 0.0,     "constr": 85000, "maint": 0.1600, "capex": 397500},
                  "elc_auto":  {"unit": "kwh", "cons": 1.677500, "prim": 1.8639,  "wtt": 0.09226, "ttw": 0.0,     "constr": 85000, "maint": 0.1600, "capex": 397500},
                  "h2_grigio": {"unit": "kg",  "cons": 0.096333, "prim": 4.5868,  "wtt": 1.05967, "ttw": 0.0,     "constr": 95000, "maint": 0.2750, "capex": 566667},
                  "h2_rete":   {"unit": "kg",  "cons": 0.096333, "prim": 11.6756, "wtt": 1.24270, "ttw": 0.0,     "constr": 95000, "maint": 0.2750, "capex": 566667},
                  "h2_verde":  {"unit": "kg",  "cons": 0.096333, "prim": 5.1787,  "wtt": 0.28900, "ttw": 0.0,     "constr": 95000, "maint": 0.2750, "capex": 566667},
              }},
    "bus_x": {"icon": "🚍", "life": 15, "km_default": 75000, "km_max": 150000,
              "vectors": {
                  "diesel":    {"unit": "l",   "cons": 0.283333, "prim": 3.2251, "wtt": 0.11220, "ttw": 0.85977, "constr": 50000, "maint": 0.2300, "capex": 227500},
                  "elc_rete":  {"unit": "kwh", "cons": 1.166667, "prim": 2.3333, "wtt": 0.25083, "ttw": 0.0,     "constr": 85000, "maint": 0.1350, "capex": 450000},
                  "elc_auto":  {"unit": "kwh", "cons": 1.166667, "prim": 1.2963, "wtt": 0.06417, "ttw": 0.0,     "constr": 85000, "maint": 0.1350, "capex": 450000},
                  "h2_grigio": {"unit": "kg",  "cons": 0.065833, "prim": 3.1346, "wtt": 0.72417, "ttw": 0.0,     "constr": 95000, "maint": 0.2200, "capex": 675000},
                  "h2_rete":   {"unit": "kg",  "cons": 0.065833, "prim": 7.9790, "wtt": 0.84925, "ttw": 0.0,     "constr": 95000, "maint": 0.2200, "capex": 675000},
                  "h2_verde":  {"unit": "kg",  "cons": 0.065833, "prim": 3.5391, "wtt": 0.19750, "ttw": 0.0,     "constr": 95000, "maint": 0.2200, "capex": 675000},
              }},
}

# Prezzi di default (dal foglio Excel)
FUEL_DEFAULTS = {"benzina": 1.90, "diesel": 1.80, "elc_rete": 0.31, "elc_auto": 0.24,
                 "h2_grigio": 2.00, "h2_rete": 20.00, "h2_verde": 15.00}

VECTOR_ICON = {"benzina": "⛽", "diesel": "⛽", "elc_rete": "⚡", "elc_auto": "🔆",
               "h2_grigio": "💧", "h2_rete": "💧", "h2_verde": "💧"}

# ==========================================================================
# 3. STILE (a prova di tema chiaro/scuro: i testi ereditano il colore)
# ==========================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap');
.h2-sub { opacity:.7; font-size:0.96rem; margin:-4px 0 2px 0; }
.h2-recap { font-size:.82rem; opacity:.65; margin:6px 0 0 0; }
.h2-take { background:rgba(13,124,92,.13); border:1px solid rgba(13,124,92,.40);
           border-left:6px solid #0D7C5C; border-radius:12px; padding:14px 18px; margin:14px 0 6px 0; font-size:0.98rem; }
.h2-note { opacity:.6; font-size:0.8rem; margin:10px 0 2px 0; }
.h2-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:14px; margin-top:8px; }
.h2c { background:rgba(127,127,127,.10); border:1px solid rgba(127,127,127,.26);
       border-left-width:6px; border-radius:13px; padding:15px 17px 14px 17px; box-shadow:0 1px 2px rgba(0,0,0,.10); }
.h2c-top { display:flex; align-items:flex-start; justify-content:space-between; gap:10px; margin-bottom:12px; }
.h2c-name { font-weight:700; font-size:1.04rem; line-height:1.2; }
.h2c-name .ic { margin-right:6px; }
.h2c-tags { display:flex; flex-direction:column; align-items:flex-end; gap:4px; flex:0 0 auto; }
.h2c-chip { font-size:.7rem; background:rgba(127,127,127,.16); border:1px solid rgba(127,127,127,.30);
            border-radius:6px; padding:2px 8px; white-space:nowrap; opacity:.92; }
.h2c-badge { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.66rem; letter-spacing:.04em;
             text-transform:uppercase; color:#fff; padding:3px 8px; border-radius:6px; white-space:nowrap; }
.h2c-metrics { display:grid; grid-template-columns:1fr 1fr; gap:11px 16px; }
.h2m-head { display:flex; justify-content:space-between; align-items:baseline; gap:6px; margin-bottom:4px; }
.h2m-lbl { font-size:.72rem; opacity:.6; text-transform:uppercase; letter-spacing:.03em; }
.h2m-val { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.0rem; }
.h2m-bar { height:7px; border-radius:5px; background:rgba(127,127,127,.20); overflow:hidden; }
.h2m-fill { height:100%; border-radius:5px; }
@media (max-width:560px){ .h2c-metrics{ grid-template-columns:1fr; } }
.h2-bd-title { font-weight:700; font-size:0.98rem; margin:16px 0 8px 0; }
.h2-leg { display:flex; flex-wrap:wrap; gap:14px; margin-bottom:12px; }
.h2-leg span { display:flex; align-items:center; gap:6px; font-size:.78rem; opacity:.85; }
.h2-leg i { width:12px; height:12px; border-radius:3px; display:inline-block; }
.h2b-row { display:grid; grid-template-columns:225px 1fr 130px; align-items:center; gap:12px; margin-bottom:9px; }
.h2b-label { font-size:.83rem; font-weight:600; text-align:right; line-height:1.2; }
.h2b-track { display:flex; height:24px; border-radius:6px; overflow:hidden;
             background:rgba(127,127,127,.18); border:1px solid rgba(127,127,127,.28); }
.h2b-seg { height:100%; display:flex; align-items:center; justify-content:center; color:#fff;
           font-size:.69rem; font-weight:700; font-family:'Space Grotesk',sans-serif; white-space:nowrap; overflow:hidden;
           text-shadow:0 1px 1px rgba(0,0,0,.45); }
.h2b-total { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.95rem; }
.h2b-total small { opacity:.55; font-weight:500; font-size:.66rem; }
@media (max-width:560px){ .h2b-row{ grid-template-columns:120px 1fr 92px; } }
</style>
"""

# ==========================================================================
# 4. SIDEBAR
# ==========================================================================
st.sidebar.markdown(f"### {_t['case']}")
veh_labels = {_t["vehicles"][k]: k for k in VEHICLES}
veh_choice = st.sidebar.selectbox(_t["vehicle"], list(veh_labels.keys()), help=_t["vehicle_help"])
VEH = veh_labels[veh_choice]
vdata = VEHICLES[VEH]

n_mezzi = st.sidebar.number_input(_t["fleet"], min_value=1, value=5, step=1, help=_t["fleet_help"])
km_anno = st.sidebar.slider(_t["km"], 1000, vdata["km_max"], vdata["km_default"], 1000, help=_t["km_help"])
lifetime = st.sidebar.slider(_t["life"], 1, 30, vdata["life"], 1, help=_t["life_help"])

prezzi = {}
with st.sidebar.expander(_t["prices"], expanded=False):
    for fk, dv in FUEL_DEFAULTS.items():
        if fk not in vdata["vectors"]:
            continue
        prezzi[fk] = st.number_input(f"{_t['fuels'][fk]} [{_t['units'][fk]}]", value=float(dv),
                                     format="%.2f", key=f"p_{fk}")

# ==========================================================================
# 5. CALCOLO
# ==========================================================================
km_tot = n_mezzi * km_anno

def calcola(vk, v):
    cons_tot = v["cons"] * km_tot                       # unità naturali/anno (flotta)
    fuel = cons_tot * prezzi.get(vk, 0.0)               # €/anno
    maint = v["maint"] * km_tot                         # €/anno
    capex = v["capex"] * n_mezzi / lifetime             # €/anno
    tco = fuel + maint + capex
    wtt = v["wtt"] * km_tot / 1000.0                    # t CO2/anno
    ttw = v["ttw"] * km_tot / 1000.0
    constr = v["constr"] * n_mezzi / lifetime / 1000.0
    return {
        "key": vk, "Nome": _t["vectors"][vk], "icon": VECTOR_ICON[vk],
        "Consumo": v["cons"], "unit": v["unit"],
        "ConsTot": cons_tot,
        "Fuel": fuel, "Maint": maint, "CAPEx": capex, "TCO": tco,
        "EurKm": tco / km_tot if km_tot else 0.0,
        "WtT": wtt, "TtW": ttw, "Constr": constr, "CO2": wtt + ttw + constr,
        "Prim": v["prim"] * km_tot / 1000.0,            # MWh/anno
    }

df = pd.DataFrame([calcola(vk, v) for vk, v in vdata["vectors"].items()])

# ==========================================================================
# 6. HELPER GRAFICI
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

def frac_of(series, val):
    lo, hi = series.min(), series.max()
    return 0.0 if hi == lo else (val - lo) / (hi - lo)

def fmt(v, dec=0):
    s = f"{v:,.{dec}f}"
    return s.replace(",", "@").replace(".", ",").replace("@", ".")

idx_cheap = df["TCO"].idxmin()
idx_clean = df["CO2"].idxmin()

# ==========================================================================
# 7. INTESTAZIONE + MESSAGGIO CHIAVE
# ==========================================================================
st.markdown(CSS, unsafe_allow_html=True)
st.title(_t["title"])
st.markdown(f"<div class='h2-sub'>{_t['subtitle']}</div>", unsafe_allow_html=True)
st.caption(_t["credits"])
st.markdown(f"<div class='h2-recap'>{_t['fleet_recap'].format(n=n_mezzi, veh=veh_choice, tot=fmt(km_tot))}</div>",
            unsafe_allow_html=True)

take_html = _t["takeaway"].format(
    n=f"<b>{n_mezzi}</b>", veh=veh_choice, km=fmt(km_anno),
    cheap=f"<b>{df.loc[idx_cheap, 'Nome']}</b>", cheap_v=fmt(df.loc[idx_cheap, "TCO"]),
    clean=f"<b>{df.loc[idx_clean, 'Nome']}</b>", clean_v=fmt(df.loc[idx_clean, "CO2"], 1),
)
# Converte il markdown **grassetto** in HTML (il markdown non vale dentro un blocco HTML)
take_html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", take_html)
st.markdown(f"<div class='h2-take'>{take_html}</div>", unsafe_allow_html=True)

# ==========================================================================
# 8. SCHEDE
# ==========================================================================
sort_map = {_t["sort_cost"]: "TCO", _t["sort_co2"]: "CO2", _t["sort_km"]: "EurKm"}
sort_choice = st.radio(_t["sort_label"], list(sort_map.keys()), horizontal=True)
df_sorted = df.sort_values(sort_map[sort_choice])

st.markdown(f"<div class='h2-note'>{_t['note']}</div>", unsafe_allow_html=True)

def metric_block(label, value, unit, frac, ratio):
    color = lerp(frac)
    w = max(3, min(100, ratio * 100))
    u = f"<span style='font-size:.62rem;opacity:.55;font-weight:500'> {unit}</span>" if unit else ""
    return (f"<div><div class='h2m-head'><span class='h2m-lbl'>{label}</span>"
            f"<span class='h2m-val' style='color:{color}'>{value}{u}</span></div>"
            f"<div class='h2m-bar'><div class='h2m-fill' style='width:{w:.0f}%;background:{color}'></div></div></div>")

cards = ""
for i, r in df_sorted.iterrows():
    accent = lerp(frac_of(df["CO2"], r["CO2"]))
    badges = ""
    if i == idx_cheap:
        badges += f"<span class='h2c-badge' style='background:#1C7C8C'>{_t['badge_cheap']}</span>"
    if i == idx_clean:
        badges += f"<span class='h2c-badge' style='background:#0D7C5C'>{_t['badge_clean']}</span>"
    cons_lbl = f"{fmt(r['Consumo'], 3)} {_t['cons_units'][r['unit']]}"

    m1 = metric_block(_t["m_tco"], fmt(r["TCO"]), _t["u_tco"], frac_of(df["TCO"], r["TCO"]), r["TCO"] / df["TCO"].max())
    m2 = metric_block(_t["m_co2"], fmt(r["CO2"], 1), _t["u_co2"], frac_of(df["CO2"], r["CO2"]), r["CO2"] / df["CO2"].max())
    m3 = metric_block(_t["m_km"], fmt(r["EurKm"], 2), _t["u_km"], frac_of(df["EurKm"], r["EurKm"]), r["EurKm"] / df["EurKm"].max())
    m4 = metric_block(_t["m_prim"], fmt(r["Prim"]), _t["u_prim"], frac_of(df["Prim"], r["Prim"]), r["Prim"] / df["Prim"].max())

    cards += (f"<div class='h2c' style='border-left-color:{accent}'>"
              f"<div class='h2c-top'><div class='h2c-name'><span class='ic'>{r['icon']}</span>{r['Nome']}</div>"
              f"<div class='h2c-tags'>{badges}<span class='h2c-chip'>{cons_lbl}</span></div></div>"
              f"<div class='h2c-metrics'>{m1}{m2}{m3}{m4}</div></div>")

st.markdown(f"<div class='h2-grid'>{cards}</div>", unsafe_allow_html=True)

# ==========================================================================
# 9. COMPOSIZIONE (barre impilate ad alto contrasto)
# ==========================================================================
def render_breakdown(data, segments, unit, sort_col, dec=0):
    dd = data.sort_values(sort_col, ascending=False)
    totals = dd[[s[0] for s in segments]].sum(axis=1)
    max_total = totals.max() if totals.max() > 0 else 1.0
    legend = "<div class='h2-leg'>" + "".join(
        f"<span><i style='background:{c}'></i>{lbl}</span>" for _, lbl, c in segments) + "</div>"
    rows = ""
    for _, r in dd.iterrows():
        total = sum(r[s[0]] for s in segments)
        segs = ""
        for col, lbl, color in segments:
            val = r[col]
            if val <= 0:
                continue
            w_track = val / max_total * 100
            w_in = val / total * 100 if total > 0 else 0
            txt = fmt(val, dec) if w_in > 12 else ""
            segs += f"<div class='h2b-seg' style='width:{w_track:.2f}%;background:{color}'>{txt}</div>"
        rows += (f"<div class='h2b-row'><div class='h2b-label'>{r['icon']} {r['Nome']}</div>"
                 f"<div class='h2b-track'>{segs}</div>"
                 f"<div class='h2b-total'>{fmt(total, dec)} <small>{unit}</small></div></div>")
    return legend + rows

with st.expander(_t["detail"], expanded=True):
    st.markdown(f"<div class='h2-bd-title'>{_t['chart_cost']}</div>", unsafe_allow_html=True)
    seg_cost = [("CAPEx", _t["leg_capex"], "#0E6E7E"), ("Maint", _t["leg_maint"], "#C58A1A"), ("Fuel", _t["leg_fuel"], "#A33B4A")]
    st.markdown(render_breakdown(df, seg_cost, _t["u_tco"], "TCO"), unsafe_allow_html=True)

    st.markdown(f"<div class='h2-bd-title'>{_t['chart_em']}</div>", unsafe_allow_html=True)
    seg_em = [("WtT", _t["leg_wtt"], "#46586B"), ("TtW", _t["leg_ttw"], "#C2521E"), ("Constr", _t["leg_constr"], "#8A94A0")]
    st.markdown(render_breakdown(df, seg_em, _t["u_co2"], "CO2", dec=1), unsafe_allow_html=True)

# ==========================================================================
# 10. TABELLA
# ==========================================================================
with st.expander(_t["table"]):
    show = df.sort_values("TCO").copy()
    show[_t["c_cons"]] = show.apply(lambda r: f"{r['Consumo']:.3f} {_t['cons_units'][r['unit']]}", axis=1)
    show = show[["Nome", _t["c_cons"], "TCO", "EurKm", "CO2", "Prim"]].rename(columns={
        "Nome": _t["c_vec"], "TCO": _t["c_tco"], "EurKm": _t["c_km"], "CO2": _t["c_co2"], "Prim": _t["c_prim"]})
    st.dataframe(show.style.format({_t["c_tco"]: "€ {:,.0f}", _t["c_km"]: "{:.2f}",
                                    _t["c_co2"]: "{:,.1f}", _t["c_prim"]: "{:,.0f}"}),
                 use_container_width=True, hide_index=True)
