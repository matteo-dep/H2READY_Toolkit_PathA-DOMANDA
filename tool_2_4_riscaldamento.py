"""
H2READY TOOLKIT - Tool 2.4: Confronto sistemi di riscaldamento
Progetto Interreg Italia-Slovenia H2READY - APE FVG
Autore: Matteo De Piccoli

Struttura della pagina, nell'ordine:
  1. VERDETTO   - elettrico contro idrogeno, entrambi autoprodotti da rinnovabile
  2. GAP        - distanza dalla caldaia a metano, in euro e in CO2
  3. CONFRONTO  - valori assoluti di tutte le soluzioni, grafici e tabella
  4. MACRO      - la stessa scelta ripetuta su piu' edifici
  5. EXPORT     - trasmissione all'excelone

Schede di confronto: superfici piatte senza bordo, un solo numero grande per
scheda (quello su cui si sta ordinando) e tinta chiara riservata alle soluzioni
migliori per costo ed emissioni. Il colore lavora una volta sola, dove serve.
"""

import os
import json
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="H2READY · Tool 2.4 Riscaldamento",
                   page_icon="🔥", layout="wide")

# ==========================================================================
# 1. LINGUA
# ==========================================================================
LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

T = {
    "it": {
        "title": "🔥 Confronto sistemi di riscaldamento",
        "subtitle": "Quanto costa, quanto inquina e quanta energia serve per scaldare un edificio, a parità di calore prodotto.",
        "credits": "H2READY Toolkit · Tool 2.4 — sviluppato nel progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "scope_title": "ℹ️ Che cosa confronta questo strumento",
        "scope_md": """
Il confronto è **a parità di calore consegnato**: ogni soluzione è dimensionata per
produrre lo stesso numero di kWh termici. Ogni voce comprende acquisto ripartito sugli
anni di vita, manutenzione, vettore energetico ed emissioni di filiera, camino e costruzione.

**La legna a ciocchi non è compresa.** Costo ed emissioni dipendono da troppe variabili
non generalizzabili: umidità del legno, distanza di trasporto, autoconsumo o acquisto,
conduzione manuale. Il pellet è invece incluso perché standardizzato.
        """,
        "case": "🎯 Il tuo caso", "prices": "💶 Prezzi dei vettori", "pv": "☀️ Fotovoltaico",
        "macro_sb": "🏙️ Scala comunale",
        "fabbisogno": "Calore necessario all'anno [kWh]",
        "fabbisogno_help": "Energia termica per scaldare l'edificio in un anno. Una casa media sta sui 10.000 kWh.",
        "lifetime": "Durata dell'impianto [anni]",
        "cop": "Resa della pompa di calore (COP)",
        "cop_help": "Unità di calore prodotte per ogni unità di elettricità.",
        "pv_yield": "Producibilità FV [kWh/kWp/anno]",
        "pv_yield_help": "In Friuli Venezia Giulia un impianto ben esposto sta fra 1.100 e 1.250.",
        "pv_area": "Superficie per kWp [m²]",
        "pv_area_help": "Moduli su tetto: circa 5 m²/kWp. A terra serve circa il doppio.",
        "n_edifici": "Numero di edifici da convertire",
        # --- verdetto ---
        "v_title": "① Verdetto di fattibilità operativa",
        "v_sub": "Pompa di calore e caldaia a idrogeno partono dalla stessa risorsa: elettricità rinnovabile autoprodotta. Cambia quanta ne serve, e quindi quanto impianto va costruito.",
        "v_pdc": "Pompa di calore", "v_h2": "Caldaia a idrogeno verde",
        "v_el": "Elettricità rinnovabile", "v_kwp": "Fotovoltaico da installare",
        "v_area": "Superficie di moduli", "v_h2kg": "Idrogeno da produrre",
        "v_ok": "**Praticabile.** Servono {a} m² di moduli fotovoltaici.",
        "v_ko": "**Impraticabile nella pratica.** Per lo stesso calore servono {r} volte l'energia e {a} m² di moduli, contro {a2} m² della pompa di calore.",
        "v_note": "La pompa di calore non produce calore: lo sposta dall'aria esterna, e per questo rende più di 1. L'idrogeno percorre la strada opposta e perde a ogni passaggio — elettrolisi, compressione, combustione.",
        # --- gap ---
        "g_title": "② Distanza dalla caldaia a metano",
        "g_sub": "Quanto costa in più ogni soluzione rispetto al riferimento fossile, e quanta CO₂ evita in cambio.",
        "g_ref": "Riferimento: caldaia a metano",
        "g_dcost": "Differenza di costo", "g_dco2": "CO₂ evitata", "g_eur_ton": "Costo della CO₂ evitata",
        "g_saves": "risparmia", "g_costs": "costa di più", "g_worse": "emette di più",
        "g_na": "non evita emissioni",
        "g_legend": "Sotto i 100 €/ton l'intervento regge il confronto con qualsiasi altra misura di decarbonizzazione. Sopra i 500 €/ton le stesse risorse rendono molto di più altrove.",
        # --- confronto ---
        "c_title": "③ Tutte le soluzioni a confronto",
        "sort_label": "Ordina per:", "sort_cost": "💶 Costo", "sort_co2": "🌱 Emissioni", "sort_eff": "⚡ Efficienza",
        "m_cost": "Costo annuo", "u_cost": "€/anno", "m_co2": "Emissioni", "u_co2": "kg CO₂/anno",
        "m_eff": "Efficienza (η / COP)", "m_prim": "Energia primaria", "u_prim": "kWh/anno",
        "badge_cheap": "più economico", "badge_clean": "più pulito",
        "detail": "📊 Da cosa derivano costi ed emissioni",
        "chart_cost": "Composizione del costo annuo [€/anno]",
        "chart_em": "Composizione delle emissioni annue [kg CO₂/anno]",
        "leg_capex": "Acquisto (diviso per gli anni)", "leg_maint": "Manutenzione", "leg_fuel": "Vettore energetico",
        "leg_wtt": "Filiera (WtT)", "leg_ttw": "Camino (TtW)", "leg_constr": "Costruzione (divisa per gli anni)",
        "table": "📋 Tabella dati completa",
        "c_tech": "Soluzione", "c_prim": "Energia primaria", "c_eff": "η / COP", "c_em": "CO₂/anno", "c_cost": "Costo/anno",
        "note": "💡 In evidenza il valore su cui stai ordinando. Sono colorate soltanto le soluzioni migliori per costo ed emissioni.",
        # --- macro ---
        "mm_title": "④ Analisi macro",
        "mm_sub": "La stessa scelta ripetuta su {n} edifici dello stesso tipo.",
        "mm_cost": "Costo annuo complessivo", "mm_co2": "CO₂ evitata complessiva",
        "mm_el": "Elettricità rinnovabile necessaria", "mm_area": "Superficie fotovoltaica",
        "mm_h2": "Idrogeno da produrre",
        "mm_hint": "Il fabbisogno di idrogeno alla scala comunale è il dato che serve al percorso B (tool 2.5 e 2.6) per dimensionare la produzione.",
        # --- export ---
        "e_title": "💾 Esportazione", "e_id": "Codice identificativo del Comune (es. 030043):",
        "e_btn": "💾 Esporta nel database centrale", "e_noid": "Inserisci il codice identificativo prima di procedere.",
        "e_ok": "✅ Dati trasmessi correttamente.", "e_err": "Errore di sincronizzazione (codice {c})",
        "e_conn": "Errore di connessione: {e}",
        "e_timeout": "⏳ Il server non ha risposto in tempo. Quasi sempre significa che i dati sono stati scritti: controlla il foglio prima di ripetere l'invio.",
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
        "subtitle": "Cost, emissions and energy needed to heat a building, at equal heat delivered.",
        "credits": "H2READY Toolkit · Tool 2.4 — developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "scope_title": "ℹ️ What this tool compares",
        "scope_md": """
The comparison is made **at equal heat delivered**: every option is sized to produce the
same thermal kWh. Each entry includes purchase spread over lifetime, maintenance, energy
carrier, and supply-chain, stack and construction emissions.

**Firewood logs are excluded.** Cost and emissions depend on too many variables that
cannot be generalised: moisture, transport distance, self-supply, manual operation.
Pellet is included, being standardised.
        """,
        "case": "🎯 Your case", "prices": "💶 Carrier prices", "pv": "☀️ Photovoltaics",
        "macro_sb": "🏙️ Municipal scale",
        "fabbisogno": "Heat needed per year [kWh]",
        "fabbisogno_help": "Thermal energy to heat the building for one year. An average home is around 10,000 kWh.",
        "lifetime": "System lifetime [years]",
        "cop": "Heat pump performance (COP)",
        "cop_help": "Units of heat produced per unit of electricity.",
        "pv_yield": "PV yield [kWh/kWp/year]",
        "pv_yield_help": "In Friuli Venezia Giulia a well-oriented system delivers 1,100–1,250.",
        "pv_area": "Area per kWp [m²]",
        "pv_area_help": "Rooftop modules: about 5 m²/kWp. Ground-mounted needs roughly double.",
        "n_edifici": "Number of buildings to convert",
        "v_title": "① Operational feasibility verdict",
        "v_sub": "Heat pump and hydrogen boiler start from the same resource: self-produced renewable electricity. What differs is how much is needed, and therefore how much plant must be built.",
        "v_pdc": "Heat pump", "v_h2": "Green hydrogen boiler",
        "v_el": "Renewable electricity", "v_kwp": "PV to be installed",
        "v_area": "Module area", "v_h2kg": "Hydrogen to produce",
        "v_ok": "**Feasible.** It takes {a} m² of PV modules.",
        "v_ko": "**Not feasible in practice.** For the same heat it takes {r} times the energy and {a} m² of modules, against {a2} m² for the heat pump.",
        "v_note": "A heat pump does not produce heat: it moves it from outside air, which is why its output exceeds 1. Hydrogen takes the opposite path and loses at every step — electrolysis, compression, combustion.",
        "g_title": "② Distance from the gas boiler",
        "g_sub": "How much more each option costs against the fossil reference, and how much CO₂ it avoids in return.",
        "g_ref": "Reference: natural gas boiler",
        "g_dcost": "Cost difference", "g_dco2": "CO₂ avoided", "g_eur_ton": "Cost of avoided CO₂",
        "g_saves": "saves", "g_costs": "costs more", "g_worse": "emits more",
        "g_na": "avoids no emissions",
        "g_legend": "Below €100/ton the measure stands comparison with any other decarbonisation option. Above €500/ton the same resources deliver far more elsewhere.",
        "c_title": "③ All options compared",
        "sort_label": "Sort by:", "sort_cost": "💶 Cost", "sort_co2": "🌱 Emissions", "sort_eff": "⚡ Efficiency",
        "m_cost": "Annual cost", "u_cost": "€/yr", "m_co2": "Emissions", "u_co2": "kg CO₂/yr",
        "m_eff": "Efficiency (η / COP)", "m_prim": "Primary energy", "u_prim": "kWh/yr",
        "badge_cheap": "cheapest", "badge_clean": "cleanest",
        "detail": "📊 Where costs and emissions come from",
        "chart_cost": "Annual cost breakdown [€/yr]",
        "chart_em": "Annual emissions breakdown [kg CO₂/yr]",
        "leg_capex": "Purchase (spread over years)", "leg_maint": "Maintenance", "leg_fuel": "Energy carrier",
        "leg_wtt": "Supply chain (WtT)", "leg_ttw": "Stack (TtW)", "leg_constr": "Construction (spread over years)",
        "table": "📋 Full data table",
        "c_tech": "Option", "c_prim": "Primary energy", "c_eff": "η / COP", "c_em": "CO₂/yr", "c_cost": "Cost/yr",
        "note": "💡 The highlighted figure is the one you are sorting by. Only the best options for cost and emissions are coloured.",
        "mm_title": "④ Macro analysis",
        "mm_sub": "The same choice repeated across {n} buildings of the same type.",
        "mm_cost": "Total annual cost", "mm_co2": "Total CO₂ avoided",
        "mm_el": "Renewable electricity needed", "mm_area": "PV area",
        "mm_h2": "Hydrogen to produce",
        "mm_hint": "Municipal hydrogen demand is the figure that pathway B (tools 2.5 and 2.6) needs to size production.",
        "e_title": "💾 Export", "e_id": "Municipality identifier code (e.g. 030043):",
        "e_btn": "💾 Export to central database", "e_noid": "Enter the identifier code before proceeding.",
        "e_ok": "✅ Data transmitted successfully.", "e_err": "Synchronisation error (code {c})",
        "e_conn": "Connection error: {e}",
        "e_timeout": "⏳ The server did not answer in time. This usually means the data was written: check the sheet before resending.",
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
        "subtitle": "Strošek, emisije in potrebna energija za ogrevanje stavbe ob enaki dobavljeni toploti.",
        "credits": "H2READY Toolkit · Orodje 2.4 — razvito v projektu [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready), avtor **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "scope_title": "ℹ️ Kaj to orodje primerja",
        "scope_md": """
Primerjava poteka **ob enaki dobavljeni toploti**: vsaka rešitev je dimenzionirana za
enako količino toplotnih kWh. Vsaka postavka vključuje nabavo, porazdeljeno na leta,
vzdrževanje, energent ter emisije dobavne verige, dimnika in izdelave.

**Polena niso vključena.** Strošek in emisije so odvisni od preveč spremenljivk:
vlažnost, razdalja prevoza, lastna oskrba, ročno upravljanje. Peleti so vključeni, ker
so standardizirani.
        """,
        "case": "🎯 Vaš primer", "prices": "💶 Cene energentov", "pv": "☀️ Fotovoltaika",
        "macro_sb": "🏙️ Občinska raven",
        "fabbisogno": "Potrebna toplota na leto [kWh]",
        "fabbisogno_help": "Toplotna energija za ogrevanje stavbe v enem letu. Povprečna hiša okoli 10.000 kWh.",
        "lifetime": "Življenjska doba sistema [leta]",
        "cop": "Učinkovitost toplotne črpalke (COP)",
        "cop_help": "Enote toplote na enoto elektrike.",
        "pv_yield": "Donos FV [kWh/kWp/leto]",
        "pv_yield_help": "V Furlaniji-Julijski krajini dobro usmerjen sistem doseže 1.100–1.250.",
        "pv_area": "Površina na kWp [m²]",
        "pv_area_help": "Strešni moduli: okoli 5 m²/kWp. Na tleh približno dvakrat toliko.",
        "n_edifici": "Število stavb za pretvorbo",
        "v_title": "① Sodba o operativni izvedljivosti",
        "v_sub": "Toplotna črpalka in vodikov kotel izhajata iz istega vira: lastne obnovljive elektrike. Razlikuje se količina in s tem obseg naprav, ki jih je treba zgraditi.",
        "v_pdc": "Toplotna črpalka", "v_h2": "Kotel na zeleni vodik",
        "v_el": "Obnovljiva elektrika", "v_kwp": "FV za namestitev",
        "v_area": "Površina modulov", "v_h2kg": "Vodik za proizvodnjo",
        "v_ok": "**Izvedljivo.** Potrebnih je {a} m² fotovoltaičnih modulov.",
        "v_ko": "**V praksi neizvedljivo.** Za enako toploto je potrebno {r}-krat več energije in {a} m² modulov, proti {a2} m² pri toplotni črpalki.",
        "v_note": "Toplotna črpalka toplote ne proizvaja: prenaša jo iz zunanjega zraka, zato je njen izkoristek večji od 1. Vodik ubere nasprotno pot in izgublja na vsakem koraku — elektroliza, stiskanje, zgorevanje.",
        "g_title": "② Razlika glede na plinski kotel",
        "g_sub": "Koliko več stane vsaka rešitev v primerjavi s fosilnim izhodiščem in koliko CO₂ v zameno prihrani.",
        "g_ref": "Izhodišče: plinski kotel",
        "g_dcost": "Razlika v strošku", "g_dco2": "Prihranjen CO₂", "g_eur_ton": "Strošek prihranjenega CO₂",
        "g_saves": "prihrani", "g_costs": "stane več", "g_worse": "oddaja več",
        "g_na": "ne prihrani emisij",
        "g_legend": "Pod 100 €/tono ukrep vzdrži primerjavo s katerim koli drugim razogljičenjem. Nad 500 €/tono ista sredstva drugje prinesejo veliko več.",
        "c_title": "③ Primerjava vseh rešitev",
        "sort_label": "Razvrsti po:", "sort_cost": "💶 Strošek", "sort_co2": "🌱 Emisije", "sort_eff": "⚡ Učinkovitost",
        "m_cost": "Letni strošek", "u_cost": "€/leto", "m_co2": "Emisije", "u_co2": "kg CO₂/leto",
        "m_eff": "Učinkovitost (η / COP)", "m_prim": "Primarna energija", "u_prim": "kWh/leto",
        "badge_cheap": "najcenejše", "badge_clean": "najčistejše",
        "detail": "📊 Od kod izhajajo stroški in emisije",
        "chart_cost": "Sestava letnega stroška [€/leto]",
        "chart_em": "Sestava letnih emisij [kg CO₂/leto]",
        "leg_capex": "Nakup (porazdeljen na leta)", "leg_maint": "Vzdrževanje", "leg_fuel": "Energent",
        "leg_wtt": "Dobavna veriga (WtT)", "leg_ttw": "Dimnik (TtW)", "leg_constr": "Izdelava (porazdeljena na leta)",
        "table": "📋 Celotna tabela podatkov",
        "c_tech": "Rešitev", "c_prim": "Primarna energija", "c_eff": "η / COP", "c_em": "CO₂/leto", "c_cost": "Strošek/leto",
        "note": "💡 Poudarjena je vrednost, po kateri razvrščate. Obarvane so le najboljše rešitve glede stroška in emisij.",
        "mm_title": "④ Makro analiza",
        "mm_sub": "Enaka izbira, ponovljena na {n} stavbah iste vrste.",
        "mm_cost": "Skupni letni strošek", "mm_co2": "Skupni prihranjeni CO₂",
        "mm_el": "Potrebna obnovljiva elektrika", "mm_area": "Površina FV",
        "mm_h2": "Vodik za proizvodnjo",
        "mm_hint": "Občinsko povpraševanje po vodiku je podatek, ki ga pot B (orodji 2.5 in 2.6) potrebuje za dimenzioniranje proizvodnje.",
        "e_title": "💾 Izvoz", "e_id": "Identifikacijska koda občine (npr. 030043):",
        "e_btn": "💾 Izvozi v osrednjo bazo", "e_noid": "Pred nadaljevanjem vnesite identifikacijsko kodo.",
        "e_ok": "✅ Podatki uspešno poslani.", "e_err": "Napaka sinhronizacije (koda {c})",
        "e_conn": "Napaka povezave: {e}",
        "e_timeout": "⏳ Strežnik ni odgovoril pravočasno. Običajno to pomeni, da so podatki zapisani: preverite preglednico, preden ponovite pošiljanje.",
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
# 2. DATI INCORPORATI (fabbisogno base 10.000 kWh/anno)
# ==========================================================================
ICONS = {"boiler_oil": "🛢️", "boiler_gas": "🔥", "stove_pellet": "🪵",
         "heat_pump": "♨️", "boiler_h2": "💧"}

LHV_H2 = 33.33  # kWh per kg di idrogeno

TECHNOLOGIES = [
    {"type": "boiler_oil",   "vector": "oil",      "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 12771.392082, "wtt_base": 444.305319,  "ttw_base": 2962.035457, "constr": 1200, "maint": 225.0,      "capex": 3500,  "fuel_key": "diesel",        "is_pdc": False},
    {"type": "boiler_gas",   "vector": "ch4",      "eta_cop": 1.0, "consumo_base": 10000.000000, "en_prim_base": 10989.010989, "wtt_base": 575.000000,  "ttw_base": 2050.000000, "constr": 950,  "maint": 200.0,      "capex": 2750,  "fuel_key": "metano",        "is_pdc": False},
    {"type": "stove_pellet", "vector": "pellet",   "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 13071.895425, "wtt_base": 422.222222,  "ttw_base": 0.000000,    "constr": 650,  "maint": 300.0,      "capex": 3000,  "fuel_key": "pellet",        "is_pdc": False},
    {"type": "heat_pump",    "vector": "elc_grid", "eta_cop": 3.0, "consumo_base": 3333.333333,  "en_prim_base": 6666.666667,  "wtt_base": 716.666667,  "ttw_base": 0.000000,    "constr": 1400, "maint": 150.0,      "capex": 11500, "fuel_key": "elc_rete",      "is_pdc": True},
    {"type": "heat_pump",    "vector": "elc_self", "eta_cop": 3.0, "consumo_base": 3333.333333,  "en_prim_base": 3703.703704,  "wtt_base": 183.333333,  "ttw_base": 0.000000,    "constr": 1400, "maint": 150.0,      "capex": 11500, "fuel_key": "elc_auto",      "is_pdc": True},
    {"type": "boiler_h2",    "vector": "h2_grey",  "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 15873.015873, "wtt_base": 3667.033370, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909, "capex": 7000,  "fuel_key": "h2_grigio",     "is_pdc": False},
    {"type": "boiler_h2",    "vector": "h2_grid",  "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 40404.040404, "wtt_base": 4300.430043, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909, "capex": 7000,  "fuel_key": "h2_rete",       "is_pdc": False},
    {"type": "boiler_h2",    "vector": "h2_green", "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 17921.146953, "wtt_base": 1000.100010, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909, "capex": 7000,  "fuel_key": "h2_verde_auto", "is_pdc": False},
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
FUEL_UNITS = {"diesel": "€/l", "metano": "€/Sm³", "pellet": "€/sacco",
              "elc_rete": "€/kWh", "elc_auto": "€/kWh",
              "h2_grigio": "€/kg", "h2_rete": "€/kg", "h2_verde_auto": "€/kg"}

# ==========================================================================
# 3. STILE
#    Le tinte sono translucide e il testo eredita il colore del tema:
#    così le schede restano leggibili sia sul tema chiaro sia su quello scuro.
# ==========================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap');
.h4-sub { opacity:.7; font-size:0.96rem; margin:-4px 0 10px 0; }
.h4-note { opacity:.6; font-size:0.8rem; margin:10px 0 2px 0; }
/* schede di confronto */
.h4-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(235px,1fr)); gap:12px; margin-top:10px; }
.h4c { background:rgba(127,127,127,.09); border-radius:12px; padding:15px 17px 16px 17px; }
.h4c-best { background:rgba(29,158,117,.15); }
.h4c-name { font-weight:700; font-size:1.0rem; line-height:1.25; }
.h4c-name .ic { margin-right:6px; }
.h4c-sub { font-size:.78rem; opacity:.62; margin:2px 0 15px 0; }
.h4c-num { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.95rem; line-height:1; }
.h4c-unit { font-size:.78rem; opacity:.62; margin-top:5px; }
.h4c-flag { font-size:.72rem; font-weight:700; color:#1D9E75; letter-spacing:.02em; margin-top:9px; }
.h4c-other { font-size:.78rem; opacity:.62; margin-top:9px; }
/* verdetto */
.h4-vs { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:6px 0; }
.h4-vsc { border:1px solid rgba(127,127,127,.28); border-radius:13px; padding:16px 18px;
          background:rgba(127,127,127,.07); border-top-width:5px; }
.h4-vsc h5 { margin:0 0 10px 0; font-size:1.02rem; font-weight:700; }
.h4-vs-row { display:flex; justify-content:space-between; gap:10px; font-size:.86rem; padding:4px 0;
             border-bottom:1px solid rgba(127,127,127,.14); }
.h4-vs-row:last-child { border-bottom:none; }
.h4-vs-row b { font-family:'Space Grotesk',sans-serif; font-size:.95rem; }
.h4-verdict { border-radius:12px; padding:14px 18px; margin:12px 0 4px 0; font-size:1.0rem; }
.h4-vd-ko { background:rgba(163,59,74,.12); border:1px solid rgba(163,59,74,.38); border-left:6px solid #A33B4A; }
.h4-vd-ok { background:rgba(13,124,92,.13); border:1px solid rgba(13,124,92,.40); border-left:6px solid #0D7C5C; }
/* barre composizione */
.h4-leg { display:flex; flex-wrap:wrap; gap:14px; margin-bottom:12px; }
.h4-leg span { display:flex; align-items:center; gap:6px; font-size:.78rem; opacity:.85; }
.h4-leg i { width:12px; height:12px; border-radius:3px; display:inline-block; }
.h4b-row { display:grid; grid-template-columns:215px 1fr 118px; align-items:center; gap:12px; margin-bottom:9px; }
.h4b-label { font-size:.83rem; font-weight:600; text-align:right; line-height:1.2; }
.h4b-track { display:flex; height:24px; border-radius:6px; overflow:hidden;
             background:rgba(127,127,127,.18); border:1px solid rgba(127,127,127,.28); }
.h4b-seg { height:100%; display:flex; align-items:center; justify-content:center; color:#fff;
           font-size:.69rem; font-weight:700; font-family:'Space Grotesk',sans-serif;
           white-space:nowrap; overflow:hidden; text-shadow:0 1px 1px rgba(0,0,0,.45); }
.h4b-total { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:.95rem; }
.h4b-total small { opacity:.55; font-weight:500; font-size:.66rem; }
@media (max-width:760px){ .h4-vs{ grid-template-columns:1fr; } }
@media (max-width:560px){ .h4b-row{ grid-template-columns:120px 1fr 84px; } }
</style>
"""

# ==========================================================================
# 4. SIDEBAR
# ==========================================================================
st.sidebar.markdown(f"### {_t['case']}")
user_fabbisogno = st.sidebar.slider(_t["fabbisogno"], 2000, 50000, 10000, 1000, help=_t["fabbisogno_help"])
user_lifetime = st.sidebar.slider(_t["lifetime"], 1, 30, 20, 1)
user_cop = st.sidebar.number_input(_t["cop"], value=3.0, step=0.1, help=_t["cop_help"])

with st.sidebar.expander(_t["pv"], expanded=False):
    pv_yield = st.number_input(_t["pv_yield"], 800, 1600, 1150, 25, help=_t["pv_yield_help"])
    pv_area_kwp = st.number_input(_t["pv_area"], 3.0, 15.0, 5.0, 0.5, help=_t["pv_area_help"])

with st.sidebar.expander(_t["macro_sb"], expanded=False):
    n_edifici = st.number_input(_t["n_edifici"], 1, 5000, 20, 1)

prezzi_kwh = {}
with st.sidebar.expander(_t["prices"], expanded=False):
    for key, f in FUELS.items():
        val = st.number_input(f"{_t['fuels'][key]} [{FUEL_UNITS[key]}]",
                              value=float(f["natura"]), format="%.3f", key=f"fuel_{key}")
        prezzi_kwh[key] = val * f["factor"]

# ==========================================================================
# 5. MOTORE
# ==========================================================================
def calcola(t):
    eta = user_cop if t["is_pdc"] else t["eta_cop"]
    eta = eta if eta > 0 else 1.0
    consumo = user_fabbisogno / eta
    cb = t["consumo_base"] if t["consumo_base"] > 0 else 1.0
    scala = consumo / cb
    wtt = consumo * (t["wtt_base"] / cb)
    ttw = consumo * (t["ttw_base"] / cb)
    costruz = t["constr"] / user_lifetime
    fuel = consumo * prezzi_kwh.get(t["fuel_key"], 0.10)
    capex = t["capex"] / user_lifetime
    return {
        "type": t["type"], "vector": t["vector"], "icon": ICONS[t["type"]],
        "Nome": _t["names"][t["type"]], "Vettore": _t["vectors"][t["vector"]],
        "Consumo": consumo, "En_Primaria": t["en_prim_base"] * scala, "Eta": eta,
        "WtT": wtt, "TtW": ttw, "Costruz": costruz, "Emiss": wtt + ttw + costruz,
        "Fuel": fuel, "Maint": t["maint"], "CAPEx": capex,
        "Costo": fuel + t["maint"] + capex,
    }


df = pd.DataFrame([calcola(t) for t in TECHNOLOGIES])
df["Label"] = df["Nome"] + " · " + df["Vettore"]

idx_cheap = df["Costo"].idxmin()
idx_clean = df["Emiss"].idxmin()

r_pdc = df[(df["type"] == "heat_pump") & (df["vector"] == "elc_self")].iloc[0]
r_h2 = df[(df["type"] == "boiler_h2") & (df["vector"] == "h2_green")].iloc[0]
r_gas = df[df["type"] == "boiler_gas"].iloc[0]


def fmt(v):
    return f"{v:,.0f}".replace(",", ".")


def fmt1(v):
    return f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def lerp(frac):
    """Scala verde -> rosso, usata dalla tabella della gap analysis."""
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


# ==========================================================================
# 6. INTESTAZIONE
# ==========================================================================
st.markdown(CSS, unsafe_allow_html=True)
st.title(_t["title"])
st.markdown(f"<div class='h4-sub'>{_t['subtitle']}</div>", unsafe_allow_html=True)
st.caption(_t["credits"])

with st.expander(_t["scope_title"], expanded=False):
    st.markdown(_t["scope_md"])
    if os.path.exists("ReadMe_calore.md"):
        st.markdown("---")
        with open("ReadMe_calore.md", "r", encoding="utf-8") as fh:
            st.markdown(fh.read())

# ==========================================================================
# 7. ① VERDETTO DI FATTIBILITA' OPERATIVA
# ==========================================================================
st.markdown("---")
st.subheader(_t["v_title"])
st.markdown(f"<div class='h4-sub'>{_t['v_sub']}</div>", unsafe_allow_html=True)

# L'energia primaria delle filiere autoprodotte coincide con l'elettricita'
# rinnovabile da generare: e' la base per dimensionare il fotovoltaico.
el_pdc, el_h2 = r_pdc["En_Primaria"], r_h2["En_Primaria"]
kwp_pdc, kwp_h2 = el_pdc / pv_yield, el_h2 / pv_yield
area_pdc, area_h2 = kwp_pdc * pv_area_kwp, kwp_h2 * pv_area_kwp
h2_kg = r_h2["Consumo"] / LHV_H2
rapporto = el_h2 / el_pdc if el_pdc > 0 else 0


def _vs_card(titolo, colore, righe):
    body = "".join(f"<div class='h4-vs-row'><span>{k}</span><b>{v}</b></div>" for k, v in righe)
    return (f"<div class='h4-vsc' style='border-top-color:{colore}'>"
            f"<h5>{titolo}</h5>{body}</div>")


st.markdown(
    "<div class='h4-vs'>"
    + _vs_card(f"♨️ {_t['v_pdc']}", "#0D7C5C", [
        (_t["v_el"], f"{fmt(el_pdc)} kWh/a"),
        (_t["v_kwp"], f"{fmt1(kwp_pdc)} kWp"),
        (_t["v_area"], f"{fmt(area_pdc)} m²"),
        (_t["v_h2kg"], "—"),
    ])
    + _vs_card(f"💧 {_t['v_h2']}", "#A33B4A", [
        (_t["v_el"], f"{fmt(el_h2)} kWh/a"),
        (_t["v_kwp"], f"{fmt1(kwp_h2)} kWp"),
        (_t["v_area"], f"{fmt(area_h2)} m²"),
        (_t["v_h2kg"], f"{fmt(h2_kg)} kg/a"),
    ])
    + "</div>", unsafe_allow_html=True)

if rapporto <= 1.5:
    st.markdown(f"<div class='h4-verdict h4-vd-ok'>{_t['v_ok'].format(a=fmt(area_h2))}</div>",
                unsafe_allow_html=True)
else:
    st.markdown(
        f"<div class='h4-verdict h4-vd-ko'>"
        f"{_t['v_ko'].format(r=fmt1(rapporto), a=fmt(area_h2), a2=fmt(area_pdc))}</div>",
        unsafe_allow_html=True)

st.caption(_t["v_note"])

# ==========================================================================
# 8. ② GAP ANALYSIS RISPETTO AL METANO
# ==========================================================================
st.markdown("---")
st.subheader(_t["g_title"])
st.markdown(f"<div class='h4-sub'>{_t['g_sub']}</div>", unsafe_allow_html=True)
st.caption(f"{_t['g_ref']} — {fmt(r_gas['Costo'])} {_t['u_cost']} · {fmt(r_gas['Emiss'])} {_t['u_co2']}")

gap = []
for _, r in df.iterrows():
    if r["type"] == "boiler_gas":
        continue
    d_costo = r["Costo"] - r_gas["Costo"]
    d_co2 = r_gas["Emiss"] - r["Emiss"]          # positivo = emissioni evitate
    eur_ton = (d_costo / d_co2 * 1000) if d_co2 > 0 else None
    gap.append({"Label": r["Label"], "icon": r["icon"],
                "d_costo": d_costo, "d_co2": d_co2, "eur_ton": eur_ton})

gap = sorted(gap, key=lambda g: (g["eur_ton"] is None, g["eur_ton"] if g["eur_ton"] is not None else 0))

righe_gap = []
for g in gap:
    if g["eur_ton"] is None:
        testo = _t["g_na"]
    else:
        testo = f"{fmt(g['eur_ton'])} €/ton"
    verso = _t["g_saves"] if g["d_costo"] < 0 else _t["g_costs"]
    righe_gap.append({
        _t["c_tech"]: f"{g['icon']} {g['Label']}",
        _t["g_dcost"]: f"{verso} {fmt(abs(g['d_costo']))} {_t['u_cost']}",
        _t["g_dco2"]: f"{fmt(g['d_co2'])} {_t['u_co2']}" if g["d_co2"] > 0 else _t["g_worse"],
        _t["g_eur_ton"]: testo,
    })

st.table(pd.DataFrame(righe_gap))
st.caption(_t["g_legend"])

# ==========================================================================
# 9. ③ TUTTE LE SOLUZIONI A CONFRONTO
#    Una scheda per soluzione: un solo numero grande (la metrica su cui si
#    sta ordinando) e tinta chiara riservata alle migliori per costo ed emissioni.
# ==========================================================================
st.markdown("---")
st.subheader(_t["c_title"])

sort_map = {_t["sort_cost"]: ("Costo", False), _t["sort_co2"]: ("Emiss", False), _t["sort_eff"]: ("Eta", True)}
sort_choice = st.radio(_t["sort_label"], list(sort_map.keys()), horizontal=True)
sort_col, sort_desc = sort_map[sort_choice]
df_sorted = df.sort_values(sort_col, ascending=not sort_desc)

st.markdown(f"<div class='h4-note'>{_t['note']}</div>", unsafe_allow_html=True)


def _valore_grande(r, colonna):
    """Numero in evidenza e sua unita', secondo l'ordinamento scelto."""
    if colonna == "Costo":
        return fmt(r["Costo"]), _t["u_cost"]
    if colonna == "Emiss":
        return fmt(r["Emiss"]), _t["u_co2"]
    return f"{r['Eta']:.1f}".replace(".", ","), _t["m_eff"]


def _altre_metriche(r, escluso):
    """Le altre due metriche, compatte sotto il numero grande."""
    voci = []
    if escluso != "Costo":
        voci.append(f"{fmt(r['Costo'])} {_t['u_cost']}")
    if escluso != "Emiss":
        voci.append(f"{fmt(r['Emiss'])} {_t['u_co2']}")
    if escluso != "Eta":
        voci.append("η " + f"{r['Eta']:.1f}".replace(".", ","))
    return " · ".join(voci)


cards = ""
for i, r in df_sorted.iterrows():
    is_best = i in (idx_cheap, idx_clean)

    flags = []
    if i == idx_cheap:
        flags.append(_t["badge_cheap"])
    if i == idx_clean:
        flags.append(_t["badge_clean"])
    flag_html = f"<div class='h4c-flag'>{' · '.join(flags)}</div>" if flags else ""

    valore, unita = _valore_grande(r, sort_col)
    cards += (
        f"<div class='h4c{' h4c-best' if is_best else ''}'>"
        f"<div class='h4c-name'><span class='ic'>{r['icon']}</span>{r['Nome']}</div>"
        f"<div class='h4c-sub'>{r['Vettore']}</div>"
        f"<div class='h4c-num'>{valore}</div>"
        f"<div class='h4c-unit'>{unita}</div>"
        f"{flag_html}"
        f"<div class='h4c-other'>{_altre_metriche(r, sort_col)}</div>"
        f"</div>"
    )

st.markdown(f"<div class='h4-grid'>{cards}</div>", unsafe_allow_html=True)


def render_breakdown(data, segments, unit, sort_key):
    dd = data.sort_values(sort_key, ascending=False)
    totals = dd[[s[0] for s in segments]].sum(axis=1)
    max_total = totals.max() if totals.max() > 0 else 1.0
    legend = "<div class='h4-leg'>" + "".join(
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
            txt = fmt(val) if w_in > 11 else ""
            segs += f"<div class='h4b-seg' style='width:{w_track:.2f}%;background:{color}'>{txt}</div>"
        rows += (f"<div class='h4b-row'><div class='h4b-label'>{r['icon']} {r['Label']}</div>"
                 f"<div class='h4b-track'>{segs}</div>"
                 f"<div class='h4b-total'>{fmt(total)} <small>{unit}</small></div></div>")
    return legend + rows


with st.expander(_t["detail"], expanded=True):
    st.markdown(f"**{_t['chart_cost']}**")
    st.markdown(render_breakdown(
        df, [("CAPEx", _t["leg_capex"], "#0E6E7E"), ("Maint", _t["leg_maint"], "#C58A1A"),
             ("Fuel", _t["leg_fuel"], "#A33B4A")], _t["u_cost"], "Costo"), unsafe_allow_html=True)
    st.markdown(f"**{_t['chart_em']}**")
    st.markdown(render_breakdown(
        df, [("WtT", _t["leg_wtt"], "#46586B"), ("TtW", _t["leg_ttw"], "#C2521E"),
             ("Costruz", _t["leg_constr"], "#8A94A0")], _t["u_co2"], "Emiss"), unsafe_allow_html=True)

with st.expander(_t["table"]):
    show = df.sort_values("Costo")[["Label", "En_Primaria", "Eta", "Emiss", "Costo"]].rename(columns={
        "Label": _t["c_tech"], "En_Primaria": _t["c_prim"], "Eta": _t["c_eff"],
        "Emiss": _t["c_em"], "Costo": _t["c_cost"]})
    st.dataframe(show.style.format({_t["c_prim"]: "{:,.0f}", _t["c_eff"]: "{:.2f}",
                                    _t["c_em"]: "{:,.0f}", _t["c_cost"]: "€ {:,.0f}"}),
                 use_container_width=True)

# ==========================================================================
# 10. ④ ANALISI MACRO
# ==========================================================================
st.markdown("---")
st.subheader(_t["mm_title"])
st.markdown(f"<div class='h4-sub'>{_t['mm_sub'].format(n=n_edifici)}</div>", unsafe_allow_html=True)

mc1, mc2 = st.columns(2)
for col, (nome, riga, colore, h2m) in zip(
        (mc1, mc2),
        [(f"♨️ {_t['v_pdc']}", r_pdc, "#0D7C5C", 0.0),
         (f"💧 {_t['v_h2']}", r_h2, "#A33B4A", h2_kg)]):
    with col:
        st.markdown(f"**{nome}**")
        st.metric(_t["mm_cost"], f"€ {fmt(riga['Costo'] * n_edifici)}")
        st.metric(_t["mm_co2"], f"{fmt((r_gas['Emiss'] - riga['Emiss']) * n_edifici / 1000)} ton/a")
        st.metric(_t["mm_el"], f"{fmt(riga['En_Primaria'] * n_edifici / 1000)} MWh/a")
        st.metric(_t["mm_area"], f"{fmt(riga['En_Primaria'] / pv_yield * pv_area_kwp * n_edifici)} m²")
        if h2m > 0:
            st.metric(_t["mm_h2"], f"{fmt1(h2m * n_edifici / 1000)} ton/a")

st.caption(_t["mm_hint"])

# ==========================================================================
# 11. ⑤ ESPORTAZIONE
# ==========================================================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwpP0x0hBnhOadXA43IieWg9EusAuhaafpyeXpyaStssDd7Qo-jwnuOttAllzz8r5JS/exec"

st.markdown("---")
st.subheader(_t["e_title"])

sol_economica = f'{df.loc[idx_cheap, "Nome"]} · {df.loc[idx_cheap, "Vettore"]}'
sol_pulita = f'{df.loc[idx_clean, "Nome"]} · {df.loc[idx_clean, "Vettore"]}'

codice = st.text_input(_t["e_id"], key="id_calore")

if st.button(_t["e_btn"], type="primary"):
    if not codice:
        st.error(_t["e_noid"])
    else:
        payload = {
            "ID_ISTAT": codice,
            "T24_FABBISOGNO_TERMICO_KWH_ANNO": int(user_fabbisogno),
            "T24_SOLUZIONE_OTTIMALE": sol_economica,
            "T24_SOLUZIONE_PIU_PULITA": sol_pulita,
            "T24_EMISSIONI_EVITATE_KGCO2_ANNO": round(r_gas["Emiss"] - df.loc[idx_clean, "Emiss"], 0),
        }
        try:
            resp = requests.post(WEBHOOK_URL, data=json.dumps(payload),
                                 headers={"Content-Type": "application/json"}, timeout=60)
            if resp.status_code in (200, 201):
                st.success(_t["e_ok"])
                st.caption(resp.text)
                st.balloons()
            else:
                st.error(_t["e_err"].format(c=resp.status_code))
        except requests.exceptions.ReadTimeout:
            st.warning(_t["e_timeout"])
        except Exception as e:
            st.error(_t["e_conn"].format(e=e))
