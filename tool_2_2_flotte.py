import streamlit as st
import pandas as pd
import re
import os

# ==========================================================================
# H2READY TOOLKIT - Tool 2.2: TCO & confronto flotte
# Diesel / Benzina vs Elettrico (BEV) vs Idrogeno (FCEV)
#
# Versione STANDALONE + multilingua (IT/EN/SL) + veste grafica H2READY.
# I dati tecnico-economici sono INCORPORATI nel codice e derivano dai fogli
# AUTO / CAMION / AUTOBUS Urbano / AUTOBUS ExtraUrbano del file
# "Comparison H2 elc FF.xlsx" (medie dei modelli di mercato censiti).
#
# NOVITA' DI QUESTA VERSIONE
#  - Condizioni di impiego: orografia, clima medio, lunghezza della tratta.
#    Orografia e clima agiscono da moltiplicatori sul consumo (e quindi su
#    costi, emissioni da carburante ed energia primaria); la tratta viene
#    confrontata con l'autonomia derata per verificare la fattibilita'.
#  - Numerazione dei risultati, coerente con l'ordinamento scelto.
#  - Prezzo H2 grigio riportato a base "alla pompa" (vedi README).
#  - Caricamento del README esterno (README_2.2_<lang>.md).
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
        "readme": "ℹ️ Come funziona questo strumento (dati, formule, ipotesi)",
        "readme_missing": "Metti il file `{f}` nella stessa cartella per vedere qui la spiegazione del funzionamento.",
        "case": "🎯 La tua flotta",
        "vehicle": "Tipo di veicolo",
        "vehicle_help": "Scegli la categoria: i consumi, i costi d'acquisto e la manutenzione cambiano molto tra un'auto e un camion.",
        "fleet": "Numero di veicoli",
        "fleet_help": "Quanti mezzi di questo tipo compongono la flotta da confrontare.",
        "km": "Chilometri all'anno per veicolo",
        "km_help": "Percorrenza media annua di un singolo mezzo. È il parametro che pesa di più sul risultato.",
        "life": "Durata del veicolo [anni]",
        "life_help": "Anni di servizio previsti. Serve a distribuire il costo d'acquisto e le emissioni di produzione del veicolo.",
        "env": "🏔️ Condizioni di impiego",
        "oro": "Orografia del percorso",
        "oro_help": "Le pendenze aumentano il consumo. I mezzi elettrici e a idrogeno recuperano parte dell'energia in discesa con la frenata rigenerativa, quindi la penalità per loro è ridotta.",
        "oro_opts": {"pianura": "Pianura", "collina": "Collina", "montagna": "Montagna"},
        "temp": "Clima medio della zona",
        "temp_help": "Il freddo penalizza soprattutto le batterie: il riscaldamento dell'abitacolo assorbe energia elettrica e la chimica della cella rende meno. Diesel e celle a combustibile scaldano con il calore di scarto, quindi perdono molto meno.",
        "temp_opts": {"mite": "Mite (> 10 °C)", "temperato": "Temperato (0–10 °C)", "rigido": "Rigido (< 0 °C)"},
        "tratta": "Tratta più lunga senza sosta [km]",
        "tratta_help": "La percorrenza massima che il mezzo deve coprire prima di potersi fermare a ricaricare o rifornire. Serve a verificare se l'autonomia basta.",
        "prices": "💶 Prezzi dei vettori energetici",
        "price_note": "⚠️ I prezzi sono **alla pompa** (comprensivi di distribuzione e compressione). Il costo di produzione dell'idrogeno grigio è molto più basso (~2 €/kg), ma non è confrontabile con gli altri valori: vedi il README.",
        "env_recap": "{oro} · {temp} · tratta {tratta} km",
        "takeaway": "Per {n} {veh} che percorrono {km} km/anno ciascuno, la soluzione **più economica** è {cheap} (circa {cheap_v} €/anno in totale) e quella **più pulita** è {clean} (circa {clean_v} t CO₂/anno).",
        "sort_label": "Ordina per:",
        "sort_cost": "💶 Costo totale", "sort_co2": "🌱 Emissioni", "sort_km": "📏 Costo per km",
        "m_tco": "Costo totale annuo", "u_tco": "€/anno",
        "m_co2": "Emissioni", "u_co2": "t CO₂/anno",
        "m_km": "Costo per km", "u_km": "€/km",
        "m_prim": "Energia primaria", "u_prim": "MWh/anno",
        "badge_cheap": "💶 più economico", "badge_clean": "🌱 più pulito",
        "note": "💡 La lunghezza delle barre indica la grandezza relativa; il <b>colore</b> dice se è un bene (verde) o un problema (rosso). Per costi, emissioni ed energia: più corto è meglio.",
        "feas_ok": "🟢 Tratta coperta", "feas_warn": "🟡 Margine ridotto", "feas_crit": "🔴 Sosta obbligatoria",
        "feas_range": "autonomia stimata {r} km",
        "detail": "📊 Da cosa derivano costi ed emissioni",
        "chart_cost": "Composizione del costo annuo della flotta [€/anno]",
        "chart_em": "Composizione delle emissioni annue [t CO₂/anno]",
        "leg_capex": "Acquisto (diviso per gli anni)", "leg_maint": "Manutenzione", "leg_fuel": "Vettore energetico",
        "leg_wtt": "Filiera (WtT)", "leg_ttw": "Scarico (TtW)", "leg_constr": "Produzione veicoli (divisa per gli anni)",
        "table": "📋 Tabella dati completa",
        "c_n": "#", "c_vec": "Alimentazione", "c_cons": "Consumo", "c_tco": "Costo/anno", "c_km": "€/km",
        "c_co2": "t CO₂/anno", "c_prim": "MWh/anno", "c_range": "Autonomia [km]",
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
        "readme": "ℹ️ How this tool works (data, formulas, assumptions)",
        "readme_missing": "Place the file `{f}` in the same folder to show the explanation here.",
        "case": "🎯 Your fleet",
        "vehicle": "Vehicle type",
        "vehicle_help": "Pick the category: consumption, purchase cost and maintenance differ widely between a car and a truck.",
        "fleet": "Number of vehicles",
        "fleet_help": "How many vehicles of this type make up the fleet being compared.",
        "km": "Kilometres per year per vehicle",
        "km_help": "Average annual distance of a single vehicle. This is the parameter with the largest impact on results.",
        "life": "Vehicle lifetime [years]",
        "life_help": "Expected years of service. Used to spread the purchase cost and the vehicle manufacturing emissions.",
        "env": "🏔️ Operating conditions",
        "oro": "Route orography",
        "oro_help": "Gradients increase consumption. Electric and hydrogen vehicles recover part of the energy downhill through regenerative braking, so their penalty is smaller.",
        "oro_opts": {"pianura": "Flat", "collina": "Hilly", "montagna": "Mountain"},
        "temp": "Average local climate",
        "temp_help": "Cold hits batteries hardest: cabin heating draws electric energy and cell chemistry performs worse. Diesel and fuel cells heat the cabin with waste heat, so they lose much less.",
        "temp_opts": {"mite": "Mild (> 10 °C)", "temperato": "Temperate (0–10 °C)", "rigido": "Harsh (< 0 °C)"},
        "tratta": "Longest leg without a stop [km]",
        "tratta_help": "The maximum distance the vehicle must cover before it can stop to recharge or refuel. Used to check whether range is sufficient.",
        "prices": "💶 Energy carrier prices",
        "price_note": "⚠️ Prices are **at the pump** (including distribution and compression). The production cost of grey hydrogen is far lower (~2 €/kg) but is not comparable with the other figures: see the README.",
        "env_recap": "{oro} · {temp} · longest leg {tratta} km",
        "takeaway": "For {n} {veh} driving {km} km/year each, the **cheapest** option is {cheap} (about {cheap_v} €/yr in total) and the **cleanest** is {clean} (about {clean_v} t CO₂/yr).",
        "sort_label": "Sort by:",
        "sort_cost": "💶 Total cost", "sort_co2": "🌱 Emissions", "sort_km": "📏 Cost per km",
        "m_tco": "Total annual cost", "u_tco": "€/yr",
        "m_co2": "Emissions", "u_co2": "t CO₂/yr",
        "m_km": "Cost per km", "u_km": "€/km",
        "m_prim": "Primary energy", "u_prim": "MWh/yr",
        "badge_cheap": "💶 cheapest", "badge_clean": "🌱 cleanest",
        "note": "💡 Bar length shows the relative size; the <b>colour</b> tells whether it's good (green) or a problem (red). For costs, emissions and energy: shorter is better.",
        "feas_ok": "🟢 Leg covered", "feas_warn": "🟡 Tight margin", "feas_crit": "🔴 Stop required",
        "feas_range": "estimated range {r} km",
        "detail": "📊 Where costs and emissions come from",
        "chart_cost": "Annual fleet cost breakdown [€/yr]",
        "chart_em": "Annual emissions breakdown [t CO₂/yr]",
        "leg_capex": "Purchase (spread over years)", "leg_maint": "Maintenance", "leg_fuel": "Energy carrier",
        "leg_wtt": "Supply chain (WtT)", "leg_ttw": "Tailpipe (TtW)", "leg_constr": "Vehicle manufacturing (spread over years)",
        "table": "📋 Full data table",
        "c_n": "#", "c_vec": "Powertrain", "c_cons": "Consumption", "c_tco": "Cost/yr", "c_km": "€/km",
        "c_co2": "t CO₂/yr", "c_prim": "MWh/yr", "c_range": "Range [km]",
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
        "readme": "ℹ️ Kako orodje deluje (podatki, formule, predpostavke)",
        "readme_missing": "Datoteko `{f}` dodajte v isto mapo, da se tu prikaže razlaga delovanja.",
        "case": "🎯 Vaš vozni park",
        "vehicle": "Vrsta vozila",
        "vehicle_help": "Izberite kategorijo: poraba, nabavna cena in vzdrževanje se med avtomobilom in tovornjakom močno razlikujejo.",
        "fleet": "Število vozil",
        "fleet_help": "Koliko vozil te vrste sestavlja vozni park, ki ga primerjate.",
        "km": "Kilometrov na leto na vozilo",
        "km_help": "Povprečna letna razdalja posameznega vozila. Ta parameter najbolj vpliva na rezultat.",
        "life": "Življenjska doba vozila [leta]",
        "life_help": "Predvidena leta uporabe. Uporablja se za porazdelitev nabavne cene in emisij izdelave vozila.",
        "env": "🏔️ Pogoji uporabe",
        "oro": "Orografija poti",
        "oro_help": "Nakloni povečajo porabo. Električna in vodikova vozila del energije pri spustu povrnejo z regenerativnim zaviranjem, zato je njihova kazen manjša.",
        "oro_opts": {"pianura": "Ravnina", "collina": "Gričevje", "montagna": "Gore"},
        "temp": "Povprečno podnebje območja",
        "temp_help": "Mraz najbolj prizadene baterije: ogrevanje kabine porablja električno energijo, kemija celice pa je manj učinkovita. Dizel in gorivne celice grejejo z odvečno toploto, zato izgubijo veliko manj.",
        "temp_opts": {"mite": "Milo (> 10 °C)", "temperato": "Zmerno (0–10 °C)", "rigido": "Ostro (< 0 °C)"},
        "tratta": "Najdaljši odsek brez postanka [km]",
        "tratta_help": "Največja razdalja, ki jo mora vozilo prevoziti, preden se lahko ustavi za polnjenje ali oskrbo. Uporablja se za preverjanje zadostnosti dosega.",
        "prices": "💶 Cene energentov",
        "price_note": "⚠️ Cene so **na točilni napravi** (vključno z distribucijo in stiskanjem). Proizvodni strošek sivega vodika je precej nižji (~2 €/kg), a ni primerljiv z drugimi vrednostmi: glejte README.",
        "env_recap": "{oro} · {temp} · odsek {tratta} km",
        "takeaway": "Za {n} {veh}, ki prevozijo {km} km/leto vsako, je **najcenejša** rešitev {cheap} (skupaj približno {cheap_v} €/leto), **najčistejša** pa {clean} (približno {clean_v} t CO₂/leto).",
        "sort_label": "Razvrsti po:",
        "sort_cost": "💶 Skupni strošek", "sort_co2": "🌱 Emisije", "sort_km": "📏 Strošek na km",
        "m_tco": "Skupni letni strošek", "u_tco": "€/leto",
        "m_co2": "Emisije", "u_co2": "t CO₂/leto",
        "m_km": "Strošek na km", "u_km": "€/km",
        "m_prim": "Primarna energija", "u_prim": "MWh/leto",
        "badge_cheap": "💶 najcenejše", "badge_clean": "🌱 najčistejše",
        "note": "💡 Dolžina stolpcev prikazuje relativno velikost; <b>barva</b> pove, ali je dobro (zeleno) ali težava (rdeče). Za stroške, emisije in energijo: krajše je bolje.",
        "feas_ok": "🟢 Odsek pokrit", "feas_warn": "🟡 Majhna rezerva", "feas_crit": "🔴 Postanek obvezen",
        "feas_range": "ocenjeni doseg {r} km",
        "detail": "📊 Od kod izhajajo stroški in emisije",
        "chart_cost": "Sestava letnega stroška voznega parka [€/leto]",
        "chart_em": "Sestava letnih emisij [t CO₂/leto]",
        "leg_capex": "Nakup (porazdeljen na leta)", "leg_maint": "Vzdrževanje", "leg_fuel": "Energent",
        "leg_wtt": "Dobavna veriga (WtT)", "leg_ttw": "Izpuh (TtW)", "leg_constr": "Izdelava vozil (porazdeljena na leta)",
        "table": "📋 Celotna tabela podatkov",
        "c_n": "#", "c_vec": "Pogon", "c_cons": "Poraba", "c_tco": "Strošek/leto", "c_km": "€/km",
        "c_co2": "t CO₂/leto", "c_prim": "MWh/leto", "c_range": "Doseg [km]",
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
#    range    = autonomia dichiarata in condizioni standard [km]  <-- DA VERIFICARE
# ==========================================================================
VEHICLES = {
    "auto":  {"icon": "🚗", "life": 20, "km_default": 15000,  "km_max": 60000,
              "tratta_default": 150, "tratta_max": 1200,
              "vectors": {
                  "benzina":   {"unit": "l",   "cons": 0.067250, "prim": 0.6925, "wtt": 0.03884, "ttw": 0.15535, "constr": 6000,  "maint": 0.0800, "capex": 41000,  "range": 800},
                  "diesel":    {"unit": "l",   "cons": 0.054000, "prim": 0.6147, "wtt": 0.02138, "ttw": 0.14256, "constr": 6000,  "maint": 0.0650, "capex": 45000,  "range": 950},
                  "elc_rete":  {"unit": "kwh", "cons": 0.136667, "prim": 0.2733, "wtt": 0.02938, "ttw": 0.0,     "constr": 12000, "maint": 0.0300, "capex": 38333, "range": 400},
                  "elc_auto":  {"unit": "kwh", "cons": 0.136667, "prim": 0.1519, "wtt": 0.00752, "ttw": 0.0,     "constr": 12000, "maint": 0.0300, "capex": 38333, "range": 400},
                  "h2_grigio": {"unit": "kg",  "cons": 0.010000, "prim": 0.4761, "wtt": 0.11000, "ttw": 0.0,     "constr": 14000, "maint": 0.0550, "capex": 67500, "range": 600},
                  "h2_rete":   {"unit": "kg",  "cons": 0.010000, "prim": 1.2120, "wtt": 0.12900, "ttw": 0.0,     "constr": 14000, "maint": 0.0550, "capex": 67500, "range": 600},
                  "h2_verde":  {"unit": "kg",  "cons": 0.010000, "prim": 0.5376, "wtt": 0.03000, "ttw": 0.0,     "constr": 14000, "maint": 0.0550, "capex": 67500, "range": 600},
              }},
    "truck": {"icon": "🚛", "life": 7, "km_default": 170000, "km_max": 300000,
              "tratta_default": 500, "tratta_max": 1500,
              "vectors": {
                  "diesel":    {"unit": "l",   "cons": 0.330000, "prim": 3.7563,  "wtt": 0.13068, "ttw": 0.87120, "constr": 60000,  "maint": 0.2500, "capex": 115000, "range": 1400},
                  "elc_rete":  {"unit": "kwh", "cons": 1.572500, "prim": 3.1450,  "wtt": 0.33809, "ttw": 0.0,     "constr": 110000, "maint": 0.1400, "capex": 245000, "range": 400},
                  "elc_auto":  {"unit": "kwh", "cons": 1.572500, "prim": 1.7472,  "wtt": 0.08649, "ttw": 0.0,     "constr": 110000, "maint": 0.1400, "capex": 245000, "range": 400},
                  "h2_grigio": {"unit": "kg",  "cons": 0.084167, "prim": 4.0075,  "wtt": 0.92583, "ttw": 0.0,     "constr": 125000, "maint": 0.2000, "capex": 400000, "range": 800},
                  "h2_rete":   {"unit": "kg",  "cons": 0.084167, "prim": 10.2010, "wtt": 1.08575, "ttw": 0.0,     "constr": 125000, "maint": 0.2000, "capex": 400000, "range": 800},
                  "h2_verde":  {"unit": "kg",  "cons": 0.084167, "prim": 4.5246,  "wtt": 0.25250, "ttw": 0.0,     "constr": 125000, "maint": 0.2000, "capex": 400000, "range": 800},
              }},
    "bus_u": {"icon": "🚌", "life": 13, "km_default": 70000, "km_max": 150000,
              "tratta_default": 200, "tratta_max": 600,
              "vectors": {
                  "diesel":    {"unit": "l",   "cons": 0.386667, "prim": 4.4014,  "wtt": 0.15312, "ttw": 1.02080, "constr": 50000, "maint": 0.3250, "capex": 213333, "range": 600},
                  "elc_rete":  {"unit": "kwh", "cons": 1.677500, "prim": 3.3550,  "wtt": 0.36066, "ttw": 0.0,     "constr": 85000, "maint": 0.1600, "capex": 397500, "range": 250},
                  "elc_auto":  {"unit": "kwh", "cons": 1.677500, "prim": 1.8639,  "wtt": 0.09226, "ttw": 0.0,     "constr": 85000, "maint": 0.1600, "capex": 397500, "range": 250},
                  "h2_grigio": {"unit": "kg",  "cons": 0.096333, "prim": 4.5868,  "wtt": 1.05967, "ttw": 0.0,     "constr": 95000, "maint": 0.2750, "capex": 566667, "range": 400},
                  "h2_rete":   {"unit": "kg",  "cons": 0.096333, "prim": 11.6756, "wtt": 1.24270, "ttw": 0.0,     "constr": 95000, "maint": 0.2750, "capex": 566667, "range": 400},
                  "h2_verde":  {"unit": "kg",  "cons": 0.096333, "prim": 5.1787,  "wtt": 0.28900, "ttw": 0.0,     "constr": 95000, "maint": 0.2750, "capex": 566667, "range": 400},
              }},
    "bus_x": {"icon": "🚍", "life": 15, "km_default": 75000, "km_max": 150000,
              "tratta_default": 300, "tratta_max": 900,
              "vectors": {
                  "diesel":    {"unit": "l",   "cons": 0.283333, "prim": 3.2251, "wtt": 0.11220, "ttw": 0.85977, "constr": 50000, "maint": 0.2300, "capex": 227500, "range": 800},
                  "elc_rete":  {"unit": "kwh", "cons": 1.166667, "prim": 2.3333, "wtt": 0.25083, "ttw": 0.0,     "constr": 85000, "maint": 0.1350, "capex": 450000, "range": 300},
                  "elc_auto":  {"unit": "kwh", "cons": 1.166667, "prim": 1.2963, "wtt": 0.06417, "ttw": 0.0,     "constr": 85000, "maint": 0.1350, "capex": 450000, "range": 300},
                  "h2_grigio": {"unit": "kg",  "cons": 0.065833, "prim": 3.1346, "wtt": 0.72417, "ttw": 0.0,     "constr": 95000, "maint": 0.2200, "capex": 675000, "range": 500},
                  "h2_rete":   {"unit": "kg",  "cons": 0.065833, "prim": 7.9790, "wtt": 0.84925, "ttw": 0.0,     "constr": 95000, "maint": 0.2200, "capex": 675000, "range": 500},
                  "h2_verde":  {"unit": "kg",  "cons": 0.065833, "prim": 3.5391, "wtt": 0.19750, "ttw": 0.0,     "constr": 95000, "maint": 0.2200, "capex": 675000, "range": 500},
              }},
}

# Prezzi di default — TUTTI su base "alla pompa/all'utente".
# NB: h2_grigio era 2.00 €/kg, che è il COSTO DI PRODUZIONE da SMR: non è
# confrontabile con gli altri prezzi e rendeva l'H2 grigio più economico del
# diesel. Portato a 10.00 €/kg (erogato a 700 bar). Vedi README.
FUEL_DEFAULTS = {"benzina": 1.90, "diesel": 1.80, "elc_rete": 0.31, "elc_auto": 0.24,
                 "h2_grigio": 10.00, "h2_rete": 20.00, "h2_verde": 15.00}

VECTOR_ICON = {"benzina": "⛽", "diesel": "⛽", "elc_rete": "⚡", "elc_auto": "🔆",
               "h2_grigio": "💧", "h2_rete": "💧", "h2_verde": "💧"}

# --- Categorie di powertrain (servono per i moltiplicatori differenziati) ---
def categoria(vk):
    if vk in ("benzina", "diesel"):
        return "ice"
    if vk.startswith("elc"):
        return "bev"
    return "fcev"

# --- Moltiplicatori delle condizioni di impiego ---
# Orografia: penalità sul consumo. I powertrain elettrici (BEV e FCEV)
# recuperano energia in discesa, quindi subiscono solo una quota della penalità.
ORO_MULT = {"pianura": 1.00, "collina": 1.15, "montagna": 1.35}
REGEN_SHARE = 0.25          # quota di penalità orografica annullata dal recupero

# Clima: il freddo penalizza molto le batterie, poco i mezzi con calore di scarto.
TEMP_MULT = {
    "ice":  {"mite": 1.00, "temperato": 1.02, "rigido": 1.05},
    "fcev": {"mite": 1.00, "temperato": 1.03, "rigido": 1.10},
    "bev":  {"mite": 1.00, "temperato": 1.08, "rigido": 1.25},
}

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
.h2c-rank { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.86rem; opacity:.45;
            margin-right:7px; letter-spacing:-.02em; }
.h2c-tags { display:flex; flex-direction:column; align-items:flex-end; gap:4px; flex:0 0 auto; }
.h2c-chip { font-size:.7rem; background:rgba(127,127,127,.16); border:1px solid rgba(127,127,127,.30);
            border-radius:6px; padding:2px 8px; white-space:nowrap; opacity:.92; }
.h2c-badge { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.66rem; letter-spacing:.04em;
             text-transform:uppercase; color:#fff; padding:3px 8px; border-radius:6px; white-space:nowrap; }
.h2c-feas { font-size:.74rem; margin-bottom:11px; opacity:.9; }
.h2c-feas small { opacity:.6; }
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

# --- Condizioni di impiego ---
st.sidebar.markdown(f"### {_t['env']}")
oro_labels = {_t["oro_opts"][k]: k for k in ORO_MULT}
oro_choice = st.sidebar.selectbox(_t["oro"], list(oro_labels.keys()), help=_t["oro_help"])
ORO = oro_labels[oro_choice]

temp_keys = ["mite", "temperato", "rigido"]
temp_labels = {_t["temp_opts"][k]: k for k in temp_keys}
temp_choice = st.sidebar.selectbox(_t["temp"], list(temp_labels.keys()), index=1, help=_t["temp_help"])
TEMP = temp_labels[temp_choice]

tratta = st.sidebar.slider(_t["tratta"], 10, vdata["tratta_max"], vdata["tratta_default"], 10,
                           help=_t["tratta_help"])

prezzi = {}
with st.sidebar.expander(_t["prices"], expanded=False):
    st.caption(_t["price_note"])
    for fk, dv in FUEL_DEFAULTS.items():
        if fk not in vdata["vectors"]:
            continue
        prezzi[fk] = st.number_input(f"{_t['fuels'][fk]} [{_t['units'][fk]}]", value=float(dv),
                                     format="%.2f", key=f"p_{fk}")

# ==========================================================================
# 5. CALCOLO
# ==========================================================================
km_tot = n_mezzi * km_anno

def mult_condizioni(cat):
    """Moltiplicatore complessivo sul consumo per orografia + clima."""
    m_oro = ORO_MULT[ORO]
    if cat in ("bev", "fcev"):
        m_oro = 1.0 + (m_oro - 1.0) * (1.0 - REGEN_SHARE)
    return m_oro * TEMP_MULT[cat][TEMP]

def valuta_tratta(range_eff):
    """Confronta la tratta più lunga con l'autonomia derata."""
    if range_eff <= 0:
        return "crit", _t["feas_crit"], "#A33B4A"
    r = tratta / range_eff
    if r <= 0.8:
        return "ok", _t["feas_ok"], "#0D7C5C"
    if r <= 1.0:
        return "warn", _t["feas_warn"], "#C98A1B"
    return "crit", _t["feas_crit"], "#A33B4A"

def calcola(vk, v):
    cat = categoria(vk)
    m = mult_condizioni(cat)

    cons_km = v["cons"] * m                             # consumo corretto per km
    cons_tot = cons_km * km_tot                         # unità naturali/anno (flotta)
    fuel = cons_tot * prezzi.get(vk, 0.0)               # €/anno
    maint = v["maint"] * km_tot                         # €/anno
    capex = v["capex"] * n_mezzi / lifetime             # €/anno
    tco = fuel + maint + capex
    wtt = v["wtt"] * m * km_tot / 1000.0                # t CO2/anno
    ttw = v["ttw"] * m * km_tot / 1000.0
    constr = v["constr"] * n_mezzi / lifetime / 1000.0  # non dipende dalle condizioni

    range_eff = v["range"] / m                          # autonomia derata
    feas_key, feas_lbl, feas_col = valuta_tratta(range_eff)

    return {
        "key": vk, "Nome": _t["vectors"][vk], "icon": VECTOR_ICON[vk], "cat": cat,
        "Consumo": cons_km, "ConsBase": v["cons"], "unit": v["unit"], "Mult": m,
        "ConsTot": cons_tot,
        "Fuel": fuel, "Maint": maint, "CAPEx": capex, "TCO": tco,
        "EurKm": tco / km_tot if km_tot else 0.0,
        "WtT": wtt, "TtW": ttw, "Constr": constr, "CO2": wtt + ttw + constr,
        "Prim": v["prim"] * m * km_tot / 1000.0,        # MWh/anno
        "Range": range_eff, "FeasKey": feas_key, "FeasLbl": feas_lbl, "FeasCol": feas_col,
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

recap = _t["fleet_recap"].format(n=n_mezzi, veh=veh_choice, tot=fmt(km_tot))
recap_env = _t["env_recap"].format(oro=oro_choice, temp=temp_choice, tratta=fmt(tratta))
st.markdown(f"<div class='h2-recap'>{recap} · {recap_env}</div>", unsafe_allow_html=True)

# --- README esterno ---
readme_file = f"README_2.2_{LANG}.md"
with st.expander(_t["readme"], expanded=False):
    if os.path.exists(readme_file):
        with open(readme_file, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info(_t["readme_missing"].format(f=readme_file))

take_html = _t["takeaway"].format(
    n=f"<b>{n_mezzi}</b>", veh=veh_choice, km=fmt(km_anno),
    cheap=f"<b>{df.loc[idx_cheap, 'Nome']}</b>", cheap_v=fmt(df.loc[idx_cheap, "TCO"]),
    clean=f"<b>{df.loc[idx_clean, 'Nome']}</b>", clean_v=fmt(df.loc[idx_clean, "CO2"], 1),
)
take_html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", take_html)
st.markdown(f"<div class='h2-take'>{take_html}</div>", unsafe_allow_html=True)

# ==========================================================================
# 8. SCHEDE (numerate secondo l'ordinamento scelto)
# ==========================================================================
sort_map = {_t["sort_cost"]: "TCO", _t["sort_co2"]: "CO2", _t["sort_km"]: "EurKm"}
sort_choice = st.radio(_t["sort_label"], list(sort_map.keys()), horizontal=True)
df_sorted = df.sort_values(sort_map[sort_choice]).reset_index()   # 'index' = indice originale

st.markdown(f"<div class='h2-note'>{_t['note']}</div>", unsafe_allow_html=True)

def metric_block(label, value, unit, frac, ratio):
    color = lerp(frac)
    w = max(3, min(100, ratio * 100))
    u = f"<span style='font-size:.62rem;opacity:.55;font-weight:500'> {unit}</span>" if unit else ""
    return (f"<div><div class='h2m-head'><span class='h2m-lbl'>{label}</span>"
            f"<span class='h2m-val' style='color:{color}'>{value}{u}</span></div>"
            f"<div class='h2m-bar'><div class='h2m-fill' style='width:{w:.0f}%;background:{color}'></div></div></div>")

cards = ""
for pos, r in df_sorted.iterrows():
    orig = r["index"]
    accent = lerp(frac_of(df["CO2"], r["CO2"]))
    badges = ""
    if orig == idx_cheap:
        badges += f"<span class='h2c-badge' style='background:#1C7C8C'>{_t['badge_cheap']}</span>"
    if orig == idx_clean:
        badges += f"<span class='h2c-badge' style='background:#0D7C5C'>{_t['badge_clean']}</span>"
    cons_lbl = f"{fmt(r['Consumo'], 3)} {_t['cons_units'][r['unit']]}"

    m1 = metric_block(_t["m_tco"], fmt(r["TCO"]), _t["u_tco"], frac_of(df["TCO"], r["TCO"]), r["TCO"] / df["TCO"].max())
    m2 = metric_block(_t["m_co2"], fmt(r["CO2"], 1), _t["u_co2"], frac_of(df["CO2"], r["CO2"]), r["CO2"] / df["CO2"].max())
    m3 = metric_block(_t["m_km"], fmt(r["EurKm"], 2), _t["u_km"], frac_of(df["EurKm"], r["EurKm"]), r["EurKm"] / df["EurKm"].max())
    m4 = metric_block(_t["m_prim"], fmt(r["Prim"]), _t["u_prim"], frac_of(df["Prim"], r["Prim"]), r["Prim"] / df["Prim"].max())

    feas = (f"<div class='h2c-feas' style='color:{r['FeasCol']}'>{r['FeasLbl']} "
            f"<small>· {_t['feas_range'].format(r=fmt(r['Range']))}</small></div>")

    cards += (f"<div class='h2c' style='border-left-color:{accent}'>"
              f"<div class='h2c-top'>"
              f"<div class='h2c-name'><span class='h2c-rank'>{pos + 1}</span>"
              f"<span class='ic'>{r['icon']}</span>{r['Nome']}</div>"
              f"<div class='h2c-tags'>{badges}<span class='h2c-chip'>{cons_lbl}</span></div></div>"
              f"{feas}"
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
# 10. TABELLA (numerata per costo crescente)
# ==========================================================================
with st.expander(_t["table"]):
    show = df.sort_values("TCO").copy().reset_index(drop=True)
    show[_t["c_n"]] = show.index + 1
    show[_t["c_cons"]] = show.apply(lambda r: f"{r['Consumo']:.3f} {_t['cons_units'][r['unit']]}", axis=1)
    show = show[[_t["c_n"], "Nome", _t["c_cons"], "TCO", "EurKm", "CO2", "Prim", "Range"]].rename(columns={
        "Nome": _t["c_vec"], "TCO": _t["c_tco"], "EurKm": _t["c_km"], "CO2": _t["c_co2"],
        "Prim": _t["c_prim"], "Range": _t["c_range"]})
    st.dataframe(show.style.format({_t["c_tco"]: "€ {:,.0f}", _t["c_km"]: "{:.2f}",
                                    _t["c_co2"]: "{:,.1f}", _t["c_prim"]: "{:,.0f}",
                                    _t["c_range"]: "{:,.0f}"}),
                 use_container_width=True, hide_index=True)
