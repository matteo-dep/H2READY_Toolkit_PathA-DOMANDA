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

st.set_page_config(page_title="H2READY toolkit - Tool 2.2", page_icon="🚗", layout="wide")

# ==========================================================================
# 0. LINGUA
#    Il selettore governa tutta l'interfaccia, non solo il manuale: fino alla
#    revisione precedente cambiava la sola lingua del file README e il resto
#    della pagina restava in italiano.
# ==========================================================================
LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_readme = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_readme]

import h2ready as H

from testi_2_2 import T
_t = T[LANG]

# Etichette tradotte delle chiavi dei dizionari di dati. Le chiavi restano in
# italiano perche' sono usate dal motore di calcolo e finiscono nell'excelone:
# si traduce solo cio' che si vede.
def vis_tec(t):
    return _t["tech"].get(t, t)


def vis_cat(c):
    return _t["catbase"].get(c, _t["tech"].get(c, c))


st.title(_t["title"])
st.markdown(_t["subtitle"])

NOME_FILE_MD = f"REadMe_Mezzi_{LANG}.md"
if os.path.exists(NOME_FILE_MD):
    with st.expander(_t["readme_exp"]):
        with open(NOME_FILE_MD, "r", encoding="utf-8") as f:
            st.markdown(f.read())
else:
    st.info(_t["readme_ko"].format(f=NOME_FILE_MD))

LINKTREE_URL = H.URL_MENU      # unico punto di verita': sta in h2ready.py


def barra_ritorno(lang_code="it"):
    """Rientro al linktree: pulsante in sidebar e link in alto a destra."""
    _lbl = _t["home"]
    try:
        st.sidebar.link_button(_lbl, LINKTREE_URL, use_container_width=True)
    except AttributeError:          # Streamlit < 1.28: resta il solo link HTML
        pass
    st.markdown(
        f"<div style='text-align:right; margin-top:-0.5rem; margin-bottom:0.5rem;'>"
        f"<a href='{LINKTREE_URL}' target='_self' "
        f"style='text-decoration:none; font-size:0.85rem; color:gray;'>{_lbl}</a>"
        f"</div>", unsafe_allow_html=True)


barra_ritorno(LANG)

# Il Comune si identifica una volta sola, qui: il codice non va piu' digitato
# in fondo alla pagina e i valori gia' raccolti sono disponibili ai calcoli.
comune = H.blocco_accesso(_t["accesso"], percorso="A", lingua=LANG)
if comune is None:
    st.stop()
H.intestazione_comune(comune)

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
    st.header(_t["sb_missione"])
    tipo_veicolo = st.selectbox(_t["lbl_veicolo"], list(VEICOLI.keys()),
                                format_func=lambda k: _t["veicoli"].get(k, k))
    V = VEICOLI[tipo_veicolo]
    km_giornalieri = st.slider(_t["lbl_km"], 10, 1000, V["km_def"], 10)
    giorni_operativi = st.slider(_t["lbl_giorni"], 200, 365, 300, 5)
    tempo_inattivita = st.slider(_t["lbl_finestra"], 0.5, 12.0, 5.0, 0.5,
                                 help=_t["help_finestra"])

    st.header(_t["sb_flotta"])
    n_veicoli = st.slider(_t["lbl_n"], 1, 500, 10, help=_t["help_n"])

    st.header(_t["sb_ambiente"])
    orografia = st.selectbox(_t["lbl_oro"], list(ORO.keys()),
                             format_func=lambda k: _t["oro"].get(k, k))
    inverno_rigido = st.checkbox(_t["lbl_inverno"], help=_t["help_inverno"])

    st.header(_t["sb_costi"])
    p_benzina = st.number_input(_t["p_benzina"], value=1.90, format="%.2f") if tipo_veicolo == "Automobile" else 0.0
    p_diesel = st.number_input(_t["p_diesel"], value=1.80, format="%.2f")
    p_el_rete = st.number_input(_t["p_el_rete"], value=0.31, format="%.3f")
    p_el_fv = st.number_input(_t["p_el_fv"], value=0.24, format="%.3f")
    p_h2_rete = st.number_input(_t["p_h2_rete"], value=20.00, format="%.2f")
    p_h2_fv = st.number_input(_t["p_h2_fv"], value=15.00, format="%.2f")
    p_ricarica_pubblica = st.number_input(_t["p_pubblica"], value=0.70, format="%.2f",
                                          help=_t["help_pubblica"])

    st.header(_t["sb_proiezioni"])
    anno_acquisto = st.slider(_t["lbl_anno"], 2024, 2035, 2024)
    anni_utilizzo = st.slider(_t["lbl_vita"], 5, 30, V["vita_def"])

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
# Etichette tradotte per i grafici: le colonne originali restano in italiano
# perche' sono chiavi di confronto nel motore di calcolo.
df_final["Tec_vis"] = df_final["Tecnologia"].map(vis_tec)
df_final["Cat_vis"] = df_final["Categoria_Base"].map(vis_cat)

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

st.subheader(_t["v_title"])
if not bev_fattibile:
    motivi = []
    if "🔴" in sem_peso:
        motivi.append(_t["v_mot_peso"].format(p=f"{peso_batt:,.0f}"))
    if "🔴" in sem_tempo:
        motivi.append(_t["v_mot_tempo"].format(t=f"{tempo_ric:.1f}", d=tempo_inattivita))
    if "🔴" in sem_aut:
        motivi.append(_t["v_mot_aut"].format(q=f"{quota_strada*100:.0f}"))
    st.error(_t["v_h2"])
    st.write(_t["v_h2_txt"].format(
        m="; ".join(motivi),
        km=f"{df_final.loc[df_final['Tecnologia']==h2_name,'Autonomia'].values[0]:,.0f}",
        min=15))
elif tco_bev <= tco_h2:
    st.success(_t["v_bev"])
    st.write(_t["v_bev_txt"].format(km=km_giornalieri, t=f"{tempo_ric:.1f}",
                                    d=tempo_inattivita, e=f"{abs(tco_h2-tco_bev):,.0f}"))
else:
    st.info(_t["v_both"])
    st.write(_t["v_both_txt"].format(e=f"{abs(tco_bev-tco_h2):,.0f}"))

if batt_limitata:
    if quota_strada > 0:
        st.warning(_t["batt_ko"].format(bt=f"{batt_teorica:,.0f}", bk=f"{batt_kwh:,.0f}",
                                        a=f"{aut_bev:,.0f}", km=km_giornalieri,
                                        q=f"{quota_strada*100:.0f}"))
    else:
        st.info(_t["batt_ok"].format(bt=f"{batt_teorica:,.0f}", bk=f"{batt_kwh:,.0f}",
                                     a=f"{aut_bev:,.0f}"))

st.markdown(_t["lim_title"])
c1, c2, c3, c4 = st.columns(4)
c1.metric(_t["m_peso"], f"{peso_batt:,.0f} kg",
          sem_peso.split()[1], delta_color="inverse")
c2.metric(_t["m_tempo"], f"{tempo_ric:.1f} h",
          _t["d_tempo"].format(d=tempo_inattivita),
          delta_color="inverse" if tempo_ric > tempo_inattivita else "normal")
c3.metric(_t["m_carico"], f"{peso_netto_perso:,.0f} kg",
          _t["d_deroga"], delta_color="inverse")
c4.metric(_t["m_delta"], f"€ {tco_h2 - tco_bev:,.0f}",
          f"{(tco_h2 - tco_bev)/total_km_life:,.2f} €/km",
          delta_color="inverse" if tco_h2 > tco_bev else "normal")

if n_sostituzioni > 0:
    st.caption(_t["sostituzioni"].format(
        km=f"{total_km_life:,.0f}", n=n_sostituzioni, v=f"{vita_batt:,.0f}",
        f=_t["sost_freddo"] if inverno_rigido else "",
        e=f"{n_sostituzioni*batt_kwh*costo_batt_kwh:,.0f}"))

# ==========================================================================
# 5. GAP ANALYSIS
# ==========================================================================
st.divider()
st.header(_t["g_title"])
st.write(_t["g_sub"].format(f=vis_tec(fossile_name), km=f"{total_km_life:,.0f}",
                            a=anni_utilizzo))

gi1, gi2 = st.columns(2)
with gi1:
    gap_bev = tco_bev - tco_fossile
    st.subheader(_t["g_bev"].format(n=vis_tec(bev_name)))
    st.metric(_t["g_tot"], f"€ {gap_bev:,.0f}", delta_color="inverse")
    st.metric(_t["g_km"], f"€ {gap_bev/total_km_life:,.3f} /km", delta_color="inverse")
    st.metric(_t["g_flotta"], f"€ {gap_bev*n_veicoli:,.0f}", delta_color="inverse")
with gi2:
    gap_h2 = tco_h2 - tco_fossile
    st.subheader(_t["g_h2"].format(n=vis_tec(h2_name)))
    st.metric(_t["g_tot"], f"€ {gap_h2:,.0f}", delta_color="inverse")
    st.metric(_t["g_km"], f"€ {gap_h2/total_km_life:,.3f} /km", delta_color="inverse")
    st.metric(_t["g_flotta"], f"€ {gap_h2*n_veicoli:,.0f}", delta_color="inverse")

# ==========================================================================
# 6. GRAFICI
# ==========================================================================
st.divider()
st.header(_t["c_title"])

df_base = df_final[df_final["Categoria_Base"].isin(
    [fossile_name, "Elettrico (BEV)", "Idrogeno (FCEV)"])].drop_duplicates(subset=["Categoria_Base"])
rif_foss = df_final[df_final["Tecnologia"] == fossile_name].iloc[0]

g1, g2 = st.columns(2)
with g1:
    st.subheader(_t["c_a"])
    f1 = px.bar(df_base, x="Cat_vis", y="Autonomia", color="Cat_vis", text_auto=".0f")
    f1.add_hline(y=rif_foss["Autonomia"], line_dash="dash", line_color="black")
    f1.update_layout(showlegend=False, xaxis_title="")
    st.plotly_chart(f1, use_container_width=True)
with g2:
    st.subheader(_t["c_b"])
    f2 = px.bar(df_base, x="Cat_vis", y="Consumo", color="Cat_vis", text_auto=".2f")
    f2.add_hline(y=rif_foss["Consumo"], line_dash="dash", line_color="black")
    f2.update_layout(showlegend=False, xaxis_title="")
    st.plotly_chart(f2, use_container_width=True)

g3, g4 = st.columns(2)
with g3:
    st.subheader(_t["c_c"])
    f3 = px.bar(df_final, x="Tec_vis", y="Eta", color="Tec_vis", text_auto=".1f")
    f3.add_hline(y=rif_foss["Eta"], line_dash="dash", line_color="black")
    f3.update_layout(showlegend=False, yaxis_title=_t["c_rendimento"], xaxis_title="")
    st.plotly_chart(f3, use_container_width=True)
with g4:
    st.subheader(_t["c_d"])
    dme = df_final.melt(id_vars="Tec_vis", value_vars=["E_Produzione", "E_Carburante"],
                        var_name=_t["c_fase"], value_name="tCO2")
    dme[_t["c_fase"]] = dme[_t["c_fase"]].replace({"E_Produzione": _t["c_costruzione"],
                                                   "E_Carburante": _t["c_uso"]})
    f4 = px.bar(dme, x="Tec_vis", y="tCO2", color=_t["c_fase"], barmode="stack",
                color_discrete_sequence=["#8E8E8E", "#D62728"])
    f4.add_hline(y=rif_foss["E_Produzione"] + rif_foss["E_Carburante"],
                 line_dash="dash", line_color="black")
    f4.update_layout(xaxis_title="")
    st.plotly_chart(f4, use_container_width=True)

st.divider()
st.subheader(_t["c_e"])
voci = ["Costo_Veicolo", "Costo_Manutenzione", "Costo_Carburante", "Costo_Batteria"]
dmc = df_final.melt(id_vars="Tec_vis", value_vars=voci,
                    var_name=_t["c_voce"], value_name="Euro")
dmc[_t["c_voce"]] = dmc[_t["c_voce"]].replace({"Costo_Veicolo": _t["c_capex"],
                                               "Costo_Manutenzione": _t["c_maint"],
                                               "Costo_Carburante": _t["c_fuel"],
                                               "Costo_Batteria": _t["c_batt"]})
f5 = px.bar(dmc, x="Tec_vis", y="Euro", color=_t["c_voce"], barmode="stack",
            color_discrete_sequence=["#0068C9", "#FFA421", "#2CA02C", "#7D3C98"])
f5.add_hline(y=tco_fossile, line_dash="dash", line_color="black",
             annotation_text=_t["c_baseline"].format(f=vis_tec(fossile_name)))
f5.update_layout(yaxis_title=_t["c_euro"], xaxis_title="")
st.plotly_chart(f5, use_container_width=True)

if V["merci"]:
    st.info(_t["payload"].format(
        b=f"{df_final.loc[df_final['Tecnologia']==bev_name,'DPay'].values[0]:.2f}",
        h=f"{df_final.loc[df_final['Tecnologia']==h2_name,'DPay'].values[0]:.2f}")
        + " · ".join(f"{r['Cat_vis']} {r['EurTkm']:.3f} €/t·km"
                     for _, r in df_base.iterrows()))

# ==========================================================================
# 7. ANALISI MACRO DI FLOTTA
# ==========================================================================
st.divider()
st.header(_t["mm_title"].format(n=n_veicoli))
st.write(_t["mm_sub"])

row_bev = df_final[df_final["Tecnologia"] == bev_name].iloc[0]
row_h2 = df_final[df_final["Tecnologia"] == h2_name].iloc[0]

cons_bev_kwh = row_bev["Cons_naturale"] * km_annui * n_veicoli
cons_h2_kg = row_h2["Cons_naturale"] * km_annui * n_veicoli
energia_elettrolizzatore = cons_h2_kg * 55.0

f1_, f2_ = st.columns(2)
with f1_:
    st.subheader(_t["mm_bev"])
    st.metric(_t["mm_el"], f"{cons_bev_kwh/1000:,.1f} MWh/a", _t["mm_el_d"])
    st.metric(_t["mm_capex"], f"€ {row_bev['Costo_Veicolo']*n_veicoli/1e6:,.2f} MLN")
    st.metric(_t["mm_opex"],
              f"€ {(row_bev['Costo_Manutenzione']+row_bev['Costo_Carburante'])/anni_utilizzo*n_veicoli/1000:,.0f} k")
with f2_:
    st.subheader(_t["mm_h2"])
    st.metric(_t["mm_massa"], f"{cons_h2_kg/1000:,.1f} t/a")
    st.metric(_t["mm_el_h2"], f"{energia_elettrolizzatore/1000:,.1f} MWh/a",
              _t["mm_diff"].format(v=f"{(energia_elettrolizzatore-cons_bev_kwh)/1000:,.1f}"),
              delta_color="inverse")
    st.metric(_t["mm_capex"], f"€ {row_h2['Costo_Veicolo']*n_veicoli/1e6:,.2f} MLN")
    st.metric(_t["mm_opex"],
              f"€ {(row_h2['Costo_Manutenzione']+row_h2['Costo_Carburante'])/anni_utilizzo*n_veicoli/1000:,.0f} k")

st.info(_t["mm_infra"])

with st.expander(_t["tab_title"]):
    show = df_final.sort_values(COSTO).copy()
    cols = {"Tec_vis": _t["tab_tec"], "Autonomia": _t["tab_aut"],
            "Consumo": _t["tab_cons"], "Eta": _t["tab_eta"],
            "TCO_Totale": _t["tab_tco"], "EurKm": _t["tab_eurkm"],
            "EurTkm": _t["tab_eurtkm"], "Payload": _t["tab_pay"]}
    st.dataframe(show[list(cols)].rename(columns=cols).style.format({
        _t["tab_aut"]: "{:,.0f}", _t["tab_cons"]: "{:.3f}",
        _t["tab_eta"]: "{:.1f}", _t["tab_tco"]: "€ {:,.0f}",
        _t["tab_eurkm"]: "{:.3f}", _t["tab_eurtkm"]: "{:.3f}",
        _t["tab_pay"]: "{:.1f}"}),
        hide_index=True)

# ==========================================================================
# 8. ESPORTAZIONE NEL DATABASE CENTRALE
# ==========================================================================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwpP0x0hBnhOadXA43IieWg9EusAuhaafpyeXpyaStssDd7Qo-jwnuOttAllzz8r5JS/exec"

st.divider()
st.header(_t["e_title"])

# L'esito prevalente riprende la logica del verdetto mostrato a schermo.
if not bev_fattibile:
    esito = "Idrogeno (unica soluzione fattibile)"
elif tco_bev <= tco_h2:
    esito = "Elettrico (BEV)"
else:
    esito = "Idrogeno (più conveniente)"

em_fossile = rif_foss["E_Produzione"] + rif_foss["E_Carburante"]
em_h2 = row_h2["E_Produzione"] + row_h2["E_Carburante"]

codice = H.testo(comune, H.COL_ID)
st.caption(_t["e_assoc"].format(c=H.testo(comune, H.COL_NOME), id=codice))

if st.button(_t["e_btn"], type="primary"):
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
    salvato = False
    try:
        resp = requests.post(WEBHOOK_URL, data=json.dumps(payload),
                             headers={"Content-Type": "application/json"}, timeout=60)
        if resp.status_code in (200, 201):
            st.success(_t["e_ok"])
            st.caption(_t["e_resp"].format(r=resp.text))
            st.balloons()
            salvato = True
        else:
            st.error(_t["e_err"].format(c=resp.status_code))
    except requests.exceptions.ReadTimeout:
        # il timeout quasi sempre arriva a scrittura gia' avvenuta
        st.warning(_t["e_timeout"])
        salvato = True
    except Exception as e:
        st.error(_t["e_conn"].format(e=e))

    if salvato:
        H.dopo_salvataggio(comune, lingua=LANG)


# Tendina "Prosegui cosi" + rientro al menu H2READY, in fondo alla pagina.
# Dopo un salvataggio riuscito e' gia' stata mostrata da dopo_salvataggio()
# e questa chiamata non fa nulla.
H.prosegui(comune, lingua=LANG)


