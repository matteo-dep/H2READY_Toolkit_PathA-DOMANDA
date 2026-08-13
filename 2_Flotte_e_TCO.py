import streamlit as st
import pandas as pd
import plotly.express as px
import math
import os
import requests
import json

# ==========================================================================
# H2READY · Tool 2.2 — Simulatore Strategico di Flotta
#
# Struttura e dashboard: versione originale del progetto.
# Motore di calcolo: rivisto sulla letteratura di progetto.
#
# COSA E' STATO CORRETTO rispetto alla versione precedente
#  1. Il moltiplicatore ambientale non è più uguale per tutte le tecnologie.
#     Prima montagna+freddo dava +81% di consumo anche al diesel. Ora il
#     termico paga poco il freddo (calore di scarto per l'abitacolo), la
#     batteria molto (riscaldamento resistivo + chimica della cella).
#     Fonti: Energies 2023,16,7142; Energy Eng. 2025,122(9) su celle LFP.
#  2. Batteria allineata a Roland Berger (2021): densità 0,176->0,233 kWh/kg,
#     costo 167->161 EUR/kWh, buffer 33% (90% SOC utile + 20% autonomia).
#  3. Detrazione peso: deroga UE +2 t per veicoli a zero emissioni
#     (Reg. UE 2019/1242) + powertrain diesel risparmiato, non 4 t.
#  4. Sostituzione della batteria: vita ~700.000 km contro 1.400.000 km di
#     motore, fuel cell e serbatoi H2 (Roland Berger). Il freddo la accorcia.
#  5. Ricarica in viaggio: se la batteria non basta per la missione
#     giornaliera, l'energia eccedente si compra a prezzo pubblico.
#  6. Verdetto calcolato, non precotto: prima decideva a priori per auto e
#     bus urbani sotto i 200 km/giorno.
#
# NON e' stato toccato (verificato corretto): contenuti energetici dei
# vettori e fattori di emissione, coerenti tra loro e con la fisica.
# ==========================================================================

st.set_page_config(page_title="H2READY toolkit - Tool 2.2 Simulatore Flotta", page_icon="🚗", layout="wide")
st.title("🚗 H2READY: Simulatore Strategico di Flotta")
st.markdown("Confronto **Diesel / Elettrico / Idrogeno** con curve di proiezione tecnologica "
            "(2024-2035) per un'analisi dinamica del TCO e delle emissioni LCA.")

LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_readme = st.sidebar.selectbox("🌐 Lingua della documentazione", list(LANG_OPTIONS.keys()),
                                   help="Cambia la lingua del manuale qui sotto. "
                                        "L'interfaccia resta in italiano.")
NOME_FILE_MD = f"REadMe_Mezzi_{LANG_OPTIONS[lang_readme]}.md"
if os.path.exists(NOME_FILE_MD):
    with st.expander("ℹ️ Leggi Istruzioni, Logiche e Assunzioni del Simulatore"):
        with open(NOME_FILE_MD, "r", encoding="utf-8") as f:
            st.markdown(f.read())
else:
    st.info(f"💡 Suggerimento: carica il file '{NOME_FILE_MD}' nella stessa cartella "
            f"per vedere qui le istruzioni.")

# ==========================================================================
# 1. DATI INCORPORATI
#    cons_kwh = energia al veicolo [kWh/km]  ·  autonomia di catalogo [km]
#    maint [€/km]  ·  capex [€]  ·  dpay = perdita di carico utile [t]
# ==========================================================================
CONV = {"Benzina": 8.76, "Diesel": 9.91, "Idrogeno": 33.33, "Elettrico": 1.0}  # kWh/unità

# Fattori di emissione WtW [kg CO2 per kWh di energia al veicolo]
F_EMISS = {"Benzina": 0.330, "Diesel": 0.307,
           "Elettrico rete": 0.215, "Elettrico autoprodotto": 0.055,
           "Idrogeno grigio": 0.330, "Idrogeno rete": 0.387, "Idrogeno autoprodotto": 0.090}

# Rendimento Tank-to-Wheel del powertrain (per il calcolo dell'efficienza WtW)
TTW = {"Fossile": 0.40, "BEV": 0.88, "H2": 0.52}

# Rendimento Well-to-Tank: dalla fonte primaria all'energia a bordo.
#  fossili   raffinazione e trasporto
#  el. rete  generazione + rete + carica    el. FV  fotovoltaico + carica
#  H2 rete   elettricità di rete -> elettrolisi (61%) -> compressione
#  H2 verde  fotovoltaico -> elettrolisi (61%) -> compressione
WTT = {"Benzina": 0.86, "Diesel": 0.86,
       "Elettrico rete": 0.50, "Elettrico autoprodotto": 0.90,
       "Idrogeno rete": 0.275, "Idrogeno autoprodotto": 0.550}

VEICOLI = {
    "Automobile": {
        "km_def": 150, "lim_peso": 400, "carica_kw": 100, "payload_t": 0.4, "merci": False,
        "tec": {
            "Benzina":                {"cons_kwh": 0.589, "aut": 800,  "maint": 0.080, "capex": 41000, "dpay": 0.00},
            "Diesel":                 {"cons_kwh": 0.535, "aut": 950,  "maint": 0.065, "capex": 45000, "dpay": 0.00},
            "Elettrico rete":         {"cons_kwh": 0.137, "aut": 400,  "maint": 0.030, "capex": 38333, "dpay": 0.30},
            "Elettrico autoprodotto": {"cons_kwh": 0.137, "aut": 400,  "maint": 0.030, "capex": 38333, "dpay": 0.30},
            "Idrogeno rete":          {"cons_kwh": 0.333, "aut": 600,  "maint": 0.055, "capex": 67500, "dpay": 0.15},
            "Idrogeno autoprodotto":  {"cons_kwh": 0.333, "aut": 600,  "maint": 0.055, "capex": 67500, "dpay": 0.15},
        },
        "constr": {"Fossile": 6000, "BEV": 12000, "H2": 14000}, "vita_def": 12},
    "Camion Pesante": {
        "km_def": 400, "lim_peso": 3500, "carica_kw": 350, "payload_t": 24.0, "merci": True,
        "tec": {
            "Diesel":                 {"cons_kwh": 3.270, "aut": 1400, "maint": 0.250, "capex": 115000, "dpay": 0.00},
            "Elettrico rete":         {"cons_kwh": 1.573, "aut": 400,  "maint": 0.140, "capex": 245000, "dpay": 3.30},
            "Elettrico autoprodotto": {"cons_kwh": 1.573, "aut": 400,  "maint": 0.140, "capex": 245000, "dpay": 3.30},
            "Idrogeno rete":          {"cons_kwh": 2.805, "aut": 800,  "maint": 0.200, "capex": 400000, "dpay": 1.53},
            "Idrogeno autoprodotto":  {"cons_kwh": 2.805, "aut": 800,  "maint": 0.200, "capex": 400000, "dpay": 1.53},
        },
        "constr": {"Fossile": 60000, "BEV": 110000, "H2": 125000}, "vita_def": 7},
    "Autobus Urbano": {
        "km_def": 200, "lim_peso": 3000, "carica_kw": 150, "payload_t": 6.0, "merci": False,
        "tec": {
            "Diesel":                 {"cons_kwh": 3.832, "aut": 600, "maint": 0.325, "capex": 213333, "dpay": 0.00},
            "Elettrico rete":         {"cons_kwh": 1.678, "aut": 250, "maint": 0.160, "capex": 397500, "dpay": 1.50},
            "Elettrico autoprodotto": {"cons_kwh": 1.678, "aut": 250, "maint": 0.160, "capex": 397500, "dpay": 1.50},
            "Idrogeno rete":          {"cons_kwh": 3.211, "aut": 400, "maint": 0.275, "capex": 566667, "dpay": 0.80},
            "Idrogeno autoprodotto":  {"cons_kwh": 3.211, "aut": 400, "maint": 0.275, "capex": 566667, "dpay": 0.80},
        },
        "constr": {"Fossile": 50000, "BEV": 85000, "H2": 95000}, "vita_def": 13},
    "Autobus Extraurbano": {
        "km_def": 300, "lim_peso": 4000, "carica_kw": 150, "payload_t": 6.0, "merci": False,
        "tec": {
            "Diesel":                 {"cons_kwh": 2.808, "aut": 800, "maint": 0.230, "capex": 227500, "dpay": 0.00},
            "Elettrico rete":         {"cons_kwh": 1.167, "aut": 300, "maint": 0.135, "capex": 450000, "dpay": 1.80},
            "Elettrico autoprodotto": {"cons_kwh": 1.167, "aut": 300, "maint": 0.135, "capex": 450000, "dpay": 1.80},
            "Idrogeno rete":          {"cons_kwh": 2.194, "aut": 500, "maint": 0.220, "capex": 675000, "dpay": 0.90},
            "Idrogeno autoprodotto":  {"cons_kwh": 2.194, "aut": 500, "maint": 0.220, "capex": 675000, "dpay": 0.90},
        },
        "constr": {"Fossile": 50000, "BEV": 85000, "H2": 95000}, "vita_def": 15},
}

def categoria(t):
    return "BEV" if "Elettrico" in t else ("H2" if "Idrogeno" in t else "Fossile")

def vettore(t):
    if t == "Benzina": return "Benzina"
    if t == "Diesel": return "Diesel"
    return "Elettrico" if "Elettrico" in t else "Idrogeno"

# --- Moltiplicatori delle condizioni di impiego (differenziati) ------------
ORO = {"Pianura": 1.00, "Collinare": 1.15, "Montagna": 1.35}
REGEN = 0.25   # i powertrain elettrici recuperano in discesa
FREDDO = {"Fossile": 1.05, "H2": 1.10, "BEV": 1.25}
VITA_FREDDO = 0.75          # il lithium plating accorcia la vita del pacco
BATT_VITA_KM = 700_000      # Roland Berger, contro 1.400.000 km del resto
BATT_BUFFER = 1.33          # 90% SOC utile + 20% margine autonomia
RIFORNIMENTO_H = {"Fossile": 10/60, "H2": 15/60}
DEROGA_UE_KG = 2000         # Reg. UE 2019/1242, veicoli a zero emissioni
POWERTRAIN_RISPARMIATO_KG = {"Automobile": 150, "Camion Pesante": 1200,
                             "Autobus Urbano": 1000, "Autobus Extraurbano": 1000}

def interpolate(year, y2024, y2030):
    if year <= 2024: return y2024
    if year >= 2030: return y2030
    return y2024 + (y2030 - y2024) * ((year - 2024) / 6)

# ==========================================================================
# 2. SIDEBAR
# ==========================================================================
with st.sidebar:
    st.header("1. Parametri di Missione")
    tipo_veicolo = st.selectbox("Tipo Veicolo", list(VEICOLI.keys()))
    V = VEICOLI[tipo_veicolo]
    km_giornalieri = st.slider("Percorrenza Giornaliera (km)", 10, 1000, V["km_def"], 10)
    giorni_operativi = st.slider("Giorni Operativi Annui", 200, 365, 300, 5)
    tempo_inattivita = st.slider("Finestra max per Ricarica (Ore)", 0.5, 12.0, 5.0, 0.5,
                                 help="Ore in cui il mezzo è fermo e disponibile a ricaricare. "
                                      "È il vincolo operativo che decide se un BEV è praticabile.")

    st.header("2. Dimensionamento Flotta")
    n_veicoli = st.slider("Numero di veicoli da sostituire", 1, 500, 10,
                          help="Definisce la dimensione della flotta per fabbisogno "
                               "energetico totale e investimenti macro.")

    st.header("3. Condizioni Ambientali")
    orografia = st.selectbox("Orografia del percorso", list(ORO.keys()))
    inverno_rigido = st.checkbox("Clima Invernale Rigido (< 0°C)",
                                 help="Penalizza soprattutto le batterie: consumano di più e "
                                      "invecchiano più in fretta (lithium plating).")

    st.header("4. Costi Energetici Iniziali (2024)")
    p_benzina = st.number_input("Benzina (€/l)", value=1.90, format="%.2f") if tipo_veicolo == "Automobile" else 0.0
    p_diesel = st.number_input("Diesel (€/l)", value=1.80, format="%.2f")
    p_el_rete = st.number_input("Elettricità Rete (€/kWh)", value=0.31, format="%.3f")
    p_el_fv = st.number_input("Elettricità FV (€/kWh)", value=0.24, format="%.3f")
    p_h2_rete = st.number_input("H2 da Rete (€/kg)", value=20.00, format="%.2f")
    p_h2_fv = st.number_input("H2 Autoprodotto (€/kg)", value=15.00, format="%.2f")
    p_ricarica_pubblica = st.number_input("Ricarica pubblica rapida (€/kWh)", value=0.70, format="%.2f",
                                          help="Usata solo per l'energia che non si riesce a "
                                               "caricare al deposito.")

    st.header("5. Proiezioni Tecnologiche")
    anno_acquisto = st.slider("Anno Previsto di Acquisto", 2024, 2035, 2024)
    anni_utilizzo = st.slider("Ciclo di Vita Utile (Anni)", 5, 30, V["vita_def"])

km_annui = km_giornalieri * giorni_operativi
total_km_life = km_annui * anni_utilizzo
fossile_name = "Benzina" if tipo_veicolo == "Automobile" else "Diesel"
bev_name = "Elettrico autoprodotto"
h2_name = "Idrogeno autoprodotto"

# ==========================================================================
# 3. MOTORE DI CALCOLO
# ==========================================================================
# Curve tecnologiche (ancorate a Roland Berger 2021)
densita_batt = interpolate(anno_acquisto, 0.176, 0.233)      # kWh/kg
costo_batt_kwh = interpolate(anno_acquisto, 167.0, 161.0)    # €/kWh
costo_fc_kw = interpolate(anno_acquisto, 330.0, 210.0)       # €/kW
m_h2_aut = interpolate(anno_acquisto, 1.0, 1.15)             # +15% autonomia H2 al 2030

def mult_env(cat):
    m = ORO[orografia]
    if cat in ("BEV", "H2"):
        m = 1.0 + (m - 1.0) * (1.0 - REGEN)
    if inverno_rigido:
        m *= FREDDO[cat]
    return m

PREZZI = {"Benzina": p_benzina, "Diesel": p_diesel, "Elettrico rete": p_el_rete,
          "Elettrico autoprodotto": p_el_fv, "Idrogeno rete": p_h2_rete,
          "Idrogeno autoprodotto": p_h2_fv}
TREND = {"Benzina": 1.1, "Diesel": 1.1, "Elettrico rete": 0.9,
         "Elettrico autoprodotto": 0.9, "Idrogeno rete": 0.6, "Idrogeno autoprodotto": 0.7}

# --- Dimensionamento della batteria sulla missione giornaliera ------------
cons_bev_km = V["tec"][bev_name]["cons_kwh"] * mult_env("BEV")
batt_teorica = km_giornalieri * cons_bev_km * BATT_BUFFER
peso_max_kg = V["lim_peso"] + DEROGA_UE_KG + POWERTRAIN_RISPARMIATO_KG[tipo_veicolo]
batt_max = peso_max_kg * densita_batt
batt_kwh = min(batt_teorica, batt_max)
batt_limitata = batt_teorica > batt_max

peso_batt = batt_kwh / densita_batt
peso_netto_perso = max(0, peso_batt - DEROGA_UE_KG - POWERTRAIN_RISPARMIATO_KG[tipo_veicolo])
aut_bev = batt_kwh / cons_bev_km if cons_bev_km else 0
tempo_ric = batt_kwh / V["carica_kw"]

# Quota di energia che il BEV non riesce a prendere al deposito
quota_strada = max(0.0, km_giornalieri - aut_bev) / km_giornalieri if km_giornalieri else 0.0

# Sostituzioni della batteria nel ciclo di vita
vita_batt = BATT_VITA_KM * (VITA_FREDDO if inverno_rigido else 1.0)
n_sostituzioni = max(0, math.ceil(total_km_life / vita_batt) - 1)

# Perdita di carico utile: per il BEV è calcolata dalla batteria realmente
# necessaria alla missione (varia con percorrenza, orografia e clima);
# per l'idrogeno si usa il valore di letteratura (Roland Berger 2021).
dpay_bev_t = peso_netto_perso / 1000.0

res = []
for t, d in V["tec"].items():
    cat = categoria(t)
    dpay = dpay_bev_t if cat == "BEV" else d["dpay"]
    m = mult_env(cat)
    cons_km = d["cons_kwh"] * m                       # kWh/km al veicolo
    vet = vettore(t)
    cons_naturale = cons_km / CONV[vet]               # l/km, kg/km o kWh/km

    # Prezzo: per il BEV una quota è comprata a colonnina pubblica
    p_base = PREZZI[t] * interpolate(anno_acquisto, 1.0, TREND[t])
    if cat == "BEV" and quota_strada > 0:
        p_eff = p_base * (1 - quota_strada) + p_ricarica_pubblica * quota_strada
    else:
        p_eff = p_base

    # Autonomia
    if cat == "BEV":
        aut = aut_bev
    elif cat == "H2":
        aut = d["aut"] * m_h2_aut / m
    else:
        aut = d["aut"] / m

    # Costi sul ciclo di vita
    fuel = cons_naturale * total_km_life * p_eff
    mnt = d["maint"] * total_km_life
    if cat == "BEV":
        # Il listino incorpora un pacco al costo di riferimento 2024 (167 €/kWh):
        # se il costo scende, il prezzo del mezzo scende in proporzione al pacco.
        cpx = max(0, d["capex"] + batt_kwh * (costo_batt_kwh - 167.0))
        repl = n_sostituzioni * batt_kwh * costo_batt_kwh
    elif cat == "H2":
        cpx = max(0, d["capex"] + {"Automobile": 100, "Camion Pesante": 300,
                                   "Autobus Urbano": 200, "Autobus Extraurbano": 200}[tipo_veicolo]
                  * (costo_fc_kw - 330.0))
        repl = 0.0
    else:
        cpx = d["capex"]
        repl = 0.0

    # Emissioni sul ciclo di vita [t CO2]
    e_prod = V["constr"][cat] / 1000.0
    e_fuel = cons_km * total_km_life * F_EMISS[t] / 1000.0

    # Efficienza Well-to-Wheel: consumo di riferimento diesel come lavoro utile
    res.append({
        "Tecnologia": t, "Categoria": cat,
        "Categoria_Base": "Elettrico (BEV)" if cat == "BEV" else
                          ("Idrogeno (FCEV)" if cat == "H2" else t),
        "Autonomia": aut, "Consumo": cons_km, "Cons_naturale": cons_naturale,
        "E_Produzione": e_prod, "E_Carburante": e_fuel,
        "Costo_Veicolo": cpx, "Costo_Manutenzione": mnt, "Costo_Carburante": fuel,
        "Costo_Batteria": repl,
        "TCO_Totale": cpx + mnt + fuel + repl,
        "Payload": max(0.1, V["payload_t"] - dpay), "DPay": dpay,
    })

df_final = pd.DataFrame(res)

# Efficienza Well-to-Wheel = rendimento della filiera × rendimento del powertrain
df_final["Eta"] = df_final.apply(
    lambda r: WTT[r["Tecnologia"]] * TTW[r["Categoria"]] * 100, axis=1)

# Costo per unità di trasporto
df_final["EurKm"] = df_final["TCO_Totale"] / total_km_life
df_final["EurTkm"] = df_final["TCO_Totale"] / (total_km_life * df_final["Payload"] * 0.6)
COSTO, U_COSTO = ("EurTkm", "€/t·km") if V["merci"] else ("EurKm", "€/km")

tco_fossile = df_final.loc[df_final["Tecnologia"] == fossile_name, "TCO_Totale"].values[0]
tco_bev = df_final.loc[df_final["Tecnologia"] == bev_name, "TCO_Totale"].values[0]
tco_h2 = df_final.loc[df_final["Tecnologia"] == h2_name, "TCO_Totale"].values[0]

# ==========================================================================
# 4. VERDETTO DI FATTIBILITA' OPERATIVA
# ==========================================================================
sem_peso = ("🟢 OK" if peso_netto_perso <= V["lim_peso"] * 0.7 else
            ("🟡 ATTENZIONE" if peso_netto_perso <= V["lim_peso"] else "🔴 CRITICO"))
sem_tempo = ("🟢 OK" if tempo_ric <= tempo_inattivita * 0.8 else
             ("🟡 ATTENZIONE" if tempo_ric <= tempo_inattivita else "🔴 CRITICO"))
sem_aut = ("🟢 OK" if quota_strada == 0 else
           ("🟡 ATTENZIONE" if quota_strada <= 0.2 else "🔴 CRITICO"))

bev_fattibile = "🔴" not in sem_peso and "🔴" not in sem_tempo and "🔴" not in sem_aut

st.subheader("📋 Verdetto di Fattibilità Operativa")
if not bev_fattibile:
    motivi = []
    if "🔴" in sem_peso: motivi.append(f"la batteria peserebbe {peso_batt:,.0f} kg")
    if "🔴" in sem_tempo: motivi.append(f"servirebbero {tempo_ric:.1f} h di ricarica "
                                        f"contro {tempo_inattivita} h disponibili")
    if "🔴" in sem_aut: motivi.append(f"il {quota_strada*100:.0f}% dell'energia andrebbe "
                                      f"comprata a colonnina pubblica")
    st.error("### 🔵 L'IDROGENO È LA SCELTA STRATEGICA MIGLIORE")
    st.write(f"L'elettrico non regge i vincoli fisici della missione: {'; '.join(motivi)}. "
             f"L'idrogeno copre {df_final.loc[df_final['Tecnologia']==h2_name,'Autonomia'].values[0]:,.0f} km "
             f"con un pieno da {(15 if 'Camion' in tipo_veicolo else 15):.0f} minuti.")
elif tco_bev <= tco_h2:
    st.success("### 🟢 L'ELETTRICO (BEV) È FATTIBILE E PIÙ ECONOMICO")
    st.write(f"La batteria copre la missione da {km_giornalieri} km e si ricarica in "
             f"{tempo_ric:.1f} h, dentro la finestra di {tempo_inattivita} h. "
             f"Costa € {abs(tco_h2-tco_bev):,.0f} in meno dell'idrogeno sul ciclo di vita.")
else:
    st.info("### 🔵 ENTRAMBE FATTIBILI: L'IDROGENO È PIÙ CONVENIENTE")
    st.write(f"L'elettrico regge i vincoli fisici, ma sul ciclo di vita l'idrogeno costa "
             f"€ {abs(tco_bev-tco_h2):,.0f} in meno.")

if batt_limitata:
    if quota_strada > 0:
        st.warning(f"⚠️ La batteria necessaria alla missione ({batt_teorica:,.0f} kWh) supera il "
                   f"limite di peso ammissibile ed è stata limitata a {batt_kwh:,.0f} kWh. "
                   f"Con {aut_bev:,.0f} km di autonomia il mezzo **non completa i "
                   f"{km_giornalieri} km della giornata**: il {quota_strada*100:.0f}% dell'energia "
                   f"va comprata a ricarica pubblica, con le soste che comporta.")
    else:
        st.info(f"ℹ️ La batteria è stata limitata dal vincolo di peso "
                f"({batt_teorica:,.0f} → {batt_kwh:,.0f} kWh). L'autonomia residua "
                f"({aut_bev:,.0f} km) copre comunque la missione, ma senza il margine "
                f"di sicurezza del 33% previsto.")

st.markdown("### 🚦 Analisi dei Limiti Fisici Elettrici (BEV)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Peso Batteria Richiesta", f"{peso_batt:,.0f} kg",
          sem_peso.split()[1], delta_color="inverse")
c2.metric("Tempo Ricarica Richiesto", f"{tempo_ric:.1f} h",
          f"vs {tempo_inattivita} h disponibili",
          delta_color="inverse" if tempo_ric > tempo_inattivita else "normal")
c3.metric("Carico Utile Perso", f"{peso_netto_perso:,.0f} kg",
          "netto deroga UE +2 t", delta_color="inverse")
c4.metric("Delta Costo H2 vs BEV", f"€ {tco_h2 - tco_bev:,.0f}",
          f"{(tco_h2 - tco_bev)/total_km_life:,.2f} €/km",
          delta_color="inverse" if tco_h2 > tco_bev else "normal")

if n_sostituzioni > 0:
    st.caption(f"🔋 Nel ciclo di vita ({total_km_life:,.0f} km) la batteria va sostituita "
               f"**{n_sostituzioni} volta/e** (vita utile {vita_batt:,.0f} km"
               f"{', ridotta dal clima rigido' if inverno_rigido else ''}): "
               f"€ {n_sostituzioni*batt_kwh*costo_batt_kwh:,.0f} per veicolo, già inclusi nel TCO.")

# ==========================================================================
# 5. GAP ANALYSIS
# ==========================================================================
st.divider()
st.header("💰 Strategia Incentivi & Gap Analysis")
st.write(f"Confronto rispetto al veicolo **{fossile_name}** per l'intero ciclo di vita "
         f"({total_km_life:,.0f} km, {anni_utilizzo} anni).")

gi1, gi2 = st.columns(2)
with gi1:
    gap_bev = tco_bev - tco_fossile
    st.subheader(f"🔋 Elettrico ({bev_name})")
    st.metric("Gap TCO Totale", f"€ {gap_bev:,.0f}", delta_color="inverse")
    st.metric("Gap al Chilometro", f"€ {gap_bev/total_km_life:,.3f} /km", delta_color="inverse")
    st.metric("Gap sull'intera flotta", f"€ {gap_bev*n_veicoli:,.0f}", delta_color="inverse")
with gi2:
    gap_h2 = tco_h2 - tco_fossile
    st.subheader(f"💧 Idrogeno ({h2_name})")
    st.metric("Gap TCO Totale", f"€ {gap_h2:,.0f}", delta_color="inverse")
    st.metric("Gap al Chilometro", f"€ {gap_h2/total_km_life:,.3f} /km", delta_color="inverse")
    st.metric("Gap sull'intera flotta", f"€ {gap_h2*n_veicoli:,.0f}", delta_color="inverse")

# ==========================================================================
# 6. GRAFICI
# ==========================================================================
st.divider()
st.header("📊 Analisi Valori Assoluti (TCO & LCA)")

df_base = df_final[df_final["Categoria_Base"].isin(
    [fossile_name, "Elettrico (BEV)", "Idrogeno (FCEV)"])].drop_duplicates(subset=["Categoria_Base"])
rif_foss = df_final[df_final["Tecnologia"] == fossile_name].iloc[0]

g1, g2 = st.columns(2)
with g1:
    st.subheader("A. Autonomia Massima [km]")
    f1 = px.bar(df_base, x="Categoria_Base", y="Autonomia", color="Categoria_Base", text_auto=".0f")
    f1.add_hline(y=rif_foss["Autonomia"], line_dash="dash", line_color="black")
    f1.update_layout(showlegend=False, xaxis_title="")
    st.plotly_chart(f1, use_container_width=True)
with g2:
    st.subheader("B. Consumo [kWh/km]")
    f2 = px.bar(df_base, x="Categoria_Base", y="Consumo", color="Categoria_Base", text_auto=".2f")
    f2.add_hline(y=rif_foss["Consumo"], line_dash="dash", line_color="black")
    f2.update_layout(showlegend=False, xaxis_title="")
    st.plotly_chart(f2, use_container_width=True)

g3, g4 = st.columns(2)
with g3:
    st.subheader("C. Efficienza Globale WtW [%]")
    f3 = px.bar(df_final, x="Tecnologia", y="Eta", color="Tecnologia", text_auto=".1f")
    f3.add_hline(y=rif_foss["Eta"], line_dash="dash", line_color="black")
    f3.update_layout(showlegend=False, yaxis_title="Rendimento %", xaxis_title="")
    st.plotly_chart(f3, use_container_width=True)
with g4:
    st.subheader("D. Emissioni LCA Totali [tCO2]")
    dme = df_final.melt(id_vars="Tecnologia", value_vars=["E_Produzione", "E_Carburante"],
                        var_name="Fase", value_name="tCO2")
    dme["Fase"] = dme["Fase"].replace({"E_Produzione": "Costruzione",
                                       "E_Carburante": "Carburante/Uso"})
    f4 = px.bar(dme, x="Tecnologia", y="tCO2", color="Fase", barmode="stack",
                color_discrete_sequence=["#8E8E8E", "#D62728"])
    f4.add_hline(y=rif_foss["E_Produzione"] + rif_foss["E_Carburante"],
                 line_dash="dash", line_color="black")
    f4.update_layout(xaxis_title="")
    st.plotly_chart(f4, use_container_width=True)

st.divider()
st.subheader("E. Costo Totale di Proprietà (TCO) Spacchettato [€]")
voci = ["Costo_Veicolo", "Costo_Manutenzione", "Costo_Carburante", "Costo_Batteria"]
dmc = df_final.melt(id_vars="Tecnologia", value_vars=voci, var_name="Voce", value_name="Euro")
dmc["Voce"] = dmc["Voce"].replace({"Costo_Veicolo": "Acquisto Mezzo (CAPEX)",
                                   "Costo_Manutenzione": "Manutenzione (OPEX)",
                                   "Costo_Carburante": "Carburante (OPEX)",
                                   "Costo_Batteria": "Sostituzione Batteria"})
f5 = px.bar(dmc, x="Tecnologia", y="Euro", color="Voce", barmode="stack",
            color_discrete_sequence=["#0068C9", "#FFA421", "#2CA02C", "#7D3C98"])
f5.add_hline(y=tco_fossile, line_dash="dash", line_color="black",
             annotation_text=f"Baseline {fossile_name}")
f5.update_layout(yaxis_title="Euro (€) nel Ciclo di Vita", xaxis_title="")
st.plotly_chart(f5, use_container_width=True)

if V["merci"]:
    st.info(f"📦 **Attenzione al carico utile.** Il mezzo elettrico perde "
            f"{df_final.loc[df_final['Tecnologia']==bev_name,'DPay'].values[0]:.2f} t di portata e "
            f"l'idrogeno {df_final.loc[df_final['Tecnologia']==h2_name,'DPay'].values[0]:.2f} t "
            f"(fonte: Roland Berger, già al netto della deroga UE). Sul costo per tonnellata "
            f"trasportata il confronto cambia: "
            + " · ".join(f"{r['Categoria_Base']} {r['EurTkm']:.3f} €/t·km"
                         for _, r in df_base.iterrows()))

# ==========================================================================
# 7. ANALISI MACRO DI FLOTTA
# ==========================================================================
st.divider()
st.header(f"🏢 Analisi Macro: Transizione Flotta Intera ({n_veicoli} veicoli)")
st.write("Aggregazione del fabbisogno energetico e dei costi annui. Evidenzia la differenza "
         "tra caricare le batterie dalla rete e produrre idrogeno verde con elettrolizzatori "
         "(efficienza: ~55 kWh per kg di H2).")

row_bev = df_final[df_final["Tecnologia"] == bev_name].iloc[0]
row_h2 = df_final[df_final["Tecnologia"] == h2_name].iloc[0]

cons_bev_kwh = row_bev["Cons_naturale"] * km_annui * n_veicoli
cons_h2_kg = row_h2["Cons_naturale"] * km_annui * n_veicoli
energia_elettrolizzatore = cons_h2_kg * 55.0

f1_, f2_ = st.columns(2)
with f1_:
    st.subheader("🔋 Scenario 100% BEV")
    st.metric("Fabbisogno Elettrico Diretto", f"{cons_bev_kwh/1000:,.1f} MWh/anno",
              "Energia per la ricarica batterie")
    st.metric("CAPEX Veicoli (Investimento)", f"€ {row_bev['Costo_Veicolo']*n_veicoli/1e6:,.2f} MLN")
    st.metric("OPEX Annuo (Energia + Maint.)",
              f"€ {(row_bev['Costo_Manutenzione']+row_bev['Costo_Carburante'])/anni_utilizzo*n_veicoli/1000:,.0f} k")
with f2_:
    st.subheader("💧 Scenario 100% Idrogeno")
    st.metric("Massa di H2 Consumata", f"{cons_h2_kg/1000:,.1f} ton/anno")
    st.metric("Fabbisogno Elettrico per H2 (FER)", f"{energia_elettrolizzatore/1000:,.1f} MWh/anno",
              f"Differenza WtW vs BEV: +{(energia_elettrolizzatore-cons_bev_kwh)/1000:,.1f} MWh",
              delta_color="inverse")
    st.metric("CAPEX Veicoli (Investimento)", f"€ {row_h2['Costo_Veicolo']*n_veicoli/1e6:,.2f} MLN")
    st.metric("OPEX Annuo (Energia + Maint.)",
              f"€ {(row_h2['Costo_Manutenzione']+row_h2['Costo_Carburante'])/anni_utilizzo*n_veicoli/1000:,.0f} k")

st.info("""
**💡 Attenzione agli oneri infrastrutturali non inclusi (ricarica / rifornimento):**
Ai costi dei mezzi va sempre sommata la costruzione dell'infrastruttura.
* **BEV:** da ~€ 2.000 (wallbox lente) a oltre € 80.000 per ogni colonnina fast/ultra-fast dedicata ai mezzi pesanti.
* **H2 (FCEV):** una HRS ad alta pressione richiede un CAPEX tra **1 e 3+ milioni di €** in funzione dei kg erogati al giorno (vedi Tool 2.8).
""")

with st.expander("📋 Tabella dati completa"):
    show = df_final.sort_values(COSTO).copy()
    cols = {"Tecnologia": "Tecnologia", "Autonomia": "Autonomia [km]",
            "Consumo": "Consumo [kWh/km]", "Eta": "Efficienza WtW [%]",
            "TCO_Totale": "TCO ciclo vita [€]", "EurKm": "€/km", "EurTkm": "€/t·km",
            "Payload": "Carico utile [t]"}
    st.dataframe(show[list(cols)].rename(columns=cols).style.format({
        "Autonomia [km]": "{:,.0f}", "Consumo [kWh/km]": "{:.3f}",
        "Efficienza WtW [%]": "{:.1f}", "TCO ciclo vita [€]": "€ {:,.0f}",
        "€/km": "{:.3f}", "€/t·km": "{:.3f}", "Carico utile [t]": "{:.1f}"}),
        hide_index=True)

# ==========================================================================
# 8. ESPORTAZIONE NEL DATABASE CENTRALE
# ==========================================================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwpP0x0hBnhOadXA43IieWg9EusAuhaafpyeXpyaStssDd7Qo-jwnuOttAllzz8r5JS/exec"

st.divider()
st.header("💾 Esportazione")

# L'esito prevalente riprende la logica del verdetto mostrato a schermo.
if not bev_fattibile:
    esito = "Idrogeno (unica soluzione fattibile)"
elif tco_bev <= tco_h2:
    esito = "Elettrico (BEV)"
else:
    esito = "Idrogeno (più conveniente)"

em_fossile = rif_foss["E_Produzione"] + rif_foss["E_Carburante"]
em_h2 = row_h2["E_Produzione"] + row_h2["E_Carburante"]

codice = st.text_input("Codice identificativo del Comune (es. 030043):", key="id_flotta")

if st.button("💾 Esporta nel database centrale", type="primary"):
    if not codice:
        st.error("Inserisci il codice identificativo prima di procedere.")
    else:
        payload = {
            "ID_ISTAT": codice,
            "T22_N_VEICOLI_ANALIZZATI": n_veicoli,
            "T22_ESITO_PREVALENTE": esito,
            "T22_BEV_FATTIBILE": "SI" if bev_fattibile else "NO",
            "T22_FABBISOGNO_H2_TON_ANNO": round(cons_h2_kg / 1000, 2),
            "T22_FABBISOGNO_ELETTRICO_MWH_ANNO": round(cons_bev_kwh / 1000, 1),
            "T22_ENERGIA_ELETTROLISI_MWH_ANNO": round(energia_elettrolizzatore / 1000, 1),
            "T22_DELTA_TCO_EURO": round(gap_h2 * n_veicoli, 0),
            "T22_EMISSIONI_EVITATE_TCO2": round((em_fossile - em_h2) * n_veicoli, 1),
        }
        try:
            resp = requests.post(WEBHOOK_URL, data=json.dumps(payload),
                                 headers={"Content-Type": "application/json"}, timeout=20)
            if response.status_code == 200:
                st.success(_t["export_success"])
                st.balloons()
                H.dopo_salvataggio(comune, lingua=LANG)      # <-- aggiungere
            else:
                st.error(f"Errore di sincronizzazione (codice {resp.status_code})")
        except Exception as e:
            st.error(f"Errore di connessione: {e}")


