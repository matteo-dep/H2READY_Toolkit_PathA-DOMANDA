import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Analisi Flotta: Elettrico vs Idrogeno",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS per lo stile dei semafori e delle schede
st.markdown("""
<style>
    .badge-green {
        background-color: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-yellow {
        background-color: #ffc107;
        color: #212529;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-red {
        background-color: #dc3545;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚦 Valutazione Comparativa Flotta: BEV (Elettrico) vs FCEV (Idrogeno)")
st.markdown("Strumento di supporto alle decisioni con sistema a semafori per l'analisi di fattibilità tecnica ed economica.")

# ---------------------------------------------------------
# 1. PARAMETRI DI INPUT (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configurazione Flotta")

tipo_veicolo = st.sidebar.selectbox(
    "Tipologia Veicoli",
    ["Auto aziendali / Unità leggere", "Furgoni / Commerciali leggeri", "Autobus urbani / Bus interurbani", "Camion / Logistica pesante"]
)

num_veicoli = st.sidebar.number_input("Numero di veicoli in flotta", min_value=1, max_value=500, value=10)
km_giornalieri = st.sidebar.slider("Chilometri giornalieri per veicolo (km/giorno)", min_value=20, max_value=800, value=150)
giorni_operativi = st.sidebar.number_input("Giorni operativi all'anno", min_value=100, max_value=365, value=250)

st.sidebar.header("⚡ Parametri Energetici e Costi")
costo_kwh = st.sidebar.number_input("Costo Elettricità (€/kWh)", min_value=0.05, max_value=1.00, value=0.25, step=0.01)
costo_h2 = st.sidebar.number_input("Costo Idrogeno alla pompa (€/kg)", min_value=5.0, max_value=25.0, value=12.0, step=0.5)

presenza_infrastruttura_h2 = st.sidebar.selectbox("Presenza Stazione H2 nelle vicinanze (<15 km)", ["Assente", "Pianificata / In progetto", "Esistente"])
potenza_rete_elettrica = st.sidebar.selectbox("Capacità Rete Elettrica nel Deposito", ["Adegua / Elevata", "Limite (Richiede upgrade)", "Insufficiente"])

# ---------------------------------------------------------
# 2. VALORI DI BENCHMARK TECNICO PER TIPOLOGIA
# ---------------------------------------------------------
benchmarks = {
    "Auto aziendali / Unità leggere": {
        "bev_cons": 0.18,  # kWh/km
        "fcev_cons": 0.01, # kg H2/km
        "bev_autonomia": 350, # km
        "fcev_autonomia": 550, # km
        "bev_tempo_ricarica": 0.75, # ore (fast charge)
        "fcev_tempo_rifornimento": 0.08, # ore (5 min)
        "bev_costo_mezzo": 40000,
        "fcev_costo_mezzo": 65000
    },
    "Furgoni / Commerciali leggeri": {
        "bev_cons": 0.28,
        "fcev_cons": 0.018,
        "bev_autonomia": 250,
        "fcev_autonomia": 450,
        "bev_tempo_ricarica": 1.0,
        "fcev_tempo_rifornimento": 0.1,
        "bev_costo_mezzo": 55000,
        "fcev_costo_mezzo": 85000
    },
    "Autobus urbani / Bus interurbani": {
        "bev_cons": 1.20,
        "fcev_cons": 0.08,
        "bev_autonomia": 220,
        "fcev_autonomia": 400,
        "bev_tempo_ricarica": 3.0,
        "fcev_tempo_rifornimento": 0.2,
        "bev_costo_mezzo": 450000,
        "fcev_costo_mezzo": 600000
    },
    "Camion / Logistica pesante": {
        "bev_cons": 1.60,
        "fcev_cons": 0.09,
        "bev_autonomia": 300,
        "fcev_autonomia": 700,
        "bev_tempo_ricarica": 4.0,
        "fcev_tempo_rifornimento": 0.25,
        "bev_costo_mezzo": 320000,
        "fcev_costo_mezzo": 480000
    }
}

b = benchmarks[tipo_veicolo]

# ---------------------------------------------------------
# 3. CALCOLI OPERATIVI ED ECONOMICI
# ---------------------------------------------------------
km_totali_anno = num_veicoli * km_giornalieri * giorni_operativi

# Consumi
kwh_anno = km_totali_anno * b["bev_cons"]
kg_h2_anno = km_totali_anno * b["fcev_cons"]

# Costi Carburante/Energia Annali
costo_energia_bev_anno = kwh_anno * costo_kwh
costo_energia_fcev_anno = kg_h2_anno * costo_h2

costo_km_bev = b["bev_cons"] * costo_kwh
costo_km_fcev = b["fcev_cons"] * costo_h2

# ---------------------------------------------------------
# 4. LOGICA SEMAFORI (VERDE / GIALLO / ROSSO)
# ---------------------------------------------------------
def get_semaforo(cond_verde, cond_giallo):
    if cond_verde:
        return "🟢 Verde", "badge-green"
    elif cond_giallo:
        return "🟡 Giallo", "badge-yellow"
    else:
        return "🔴 Rosso", "badge-red"

# Valutazioni BEV
bev_auton_ok = km_giornalieri <= (b["bev_autonomia"] * 0.8)
bev_auton_warn = km_giornalieri <= b["bev_autonomia"]
sem_bev_autonomia, class_bev_autonomia = get_semaforo(bev_auton_ok, bev_auton_warn)

sem_bev_efficienza, class_bev_efficienza = "🟢 Verde", "badge-green" # Efficienza plug-to-wheel sempre altissima (>75%)

bev_infra_ok = potenza_rete_elettrica == "Adegua / Elevata"
bev_infra_warn = potenza_rete_elettrica == "Limite (Richiede upgrade)"
sem_bev_infra, class_bev_infra = get_semaforo(bev_infra_ok, bev_infra_warn)

sem_bev_costokm, class_bev_costokm = get_semaforo(costo_km_bev < 0.15, costo_km_bev < 0.30)

# Valutazioni FCEV
fcev_auton_ok = km_giornalieri <= b["fcev_autonomia"]
fcev_auton_warn = km_giornalieri <= (b["fcev_autonomia"] * 1.2)
sem_fcev_autonomia, class_fcev_autonomia = get_semaforo(fcev_auton_ok, fcev_auton_warn)

sem_fcev_efficienza, class_fcev_efficienza = "🔴 Rosso", "badge-red" # Efficienza Power-to-Wheel bassa (~30%)

fcev_infra_ok = presenza_infrastruttura_h2 == "Esistente"
fcev_infra_warn = presenza_infrastruttura_h2 == "Pianificata / In progetto"
sem_fcev_infra, class_fcev_infra = get_semaforo(fcev_infra_ok, fcev_infra_warn)

sem_fcev_costokm, class_fcev_costokm = get_semaforo(costo_km_fcev < 0.15, costo_km_fcev < 0.30)

# Rifornimento / Operatività
sem_bev_tempo, class_bev_tempo = get_semaforo(b["bev_tempo_ricarica"] <= 1.0, b["bev_tempo_ricarica"] <= 2.5)
sem_fcev_tempo, class_fcev_tempo = "🟢 Verde", "badge-green" # Rifornimento H2 sempre veloce (<15 min)

# ---------------------------------------------------------
# 5. DASHBOARD RISULTATI
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Chilometraggio Annuo Flotta", f"{km_totali_anno:,.0f} km")
with col2:
    st.metric("Costo Elettricità al km (BEV)", f"€ {costo_km_bev:.3f} / km")
with col3:
    st.metric("Costo Idrogeno al km (FCEV)", f"€ {costo_km_fcev:.3f} / km")

st.markdown("---")
st.subheader("🚦 Matrice di Fattibilità a Semafori")

data_matrix = [
    {
        "Criterio di Valutazione": "Autonomia e Copertura Turni",
        "BEV (Elettrico)": f"<span class='{class_bev_autonomia}'>{sem_bev_autonomia}</span>",
        "Note BEV": f"Autonomia nominale ~{b['bev_autonomia']} km",
        "FCEV (Idrogeno)": f"<span class='{class_fcev_autonomia}'>{sem_fcev_autonomia}</span>",
        "Note FCEV": f"Autonomia nominale ~{b['fcev_autonomia']} km"
    },
    {
        "Criterio di Valutazione": "Tempi di Rifornimento / Ricarica",
        "BEV (Elettrico)": f"<span class='{class_bev_tempo}'>{sem_bev_tempo}</span>",
        "Note BEV": f"Ricarica: ~{b['bev_tempo_ricarica']}h",
        "FCEV (Idrogeno)": f"<span class='{class_fcev_tempo}'>{sem_fcev_tempo}</span>",
        "Note FCEV": f"Rifornimento: ~{int(b['fcev_tempo_rifornimento']*60)} min"
    },
    {
        "Criterio di Valutazione": "Disponibilità Infrastruttura",
        "BEV (Elettrico)": f"<span class='{class_bev_infra}'>{sem_bev_infra}</span>",
        "Note BEV": f"Rete locale: {potenza_rete_elettrica}",
        "FCEV (Idrogeno)": f"<span class='{class_fcev_infra}'>{sem_fcev_infra}</span>",
        "Note FCEV": f"Stazione H2: {presenza_infrastruttura_h2}"
    },
    {
        "Criterio di Valutazione": "Costo del Carburante al km",
        "BEV (Elettrico)": f"<span class='{class_bev_costokm}'>{sem_bev_costokm}</span>",
        "Note BEV": f"€ {costo_km_bev:.2f} / km",
        "FCEV (Idrogeno)": f"<span class='{class_fcev_costokm}'>{sem_fcev_costokm}</span>",
        "Note FCEV": f"€ {costo_km_fcev:.2f} / km"
    },
    {
        "Criterio di Valutazione": "Efficienza Energetica Complessiva",
        "BEV (Elettrico)": f"<span class='{class_bev_efficienza}'>{sem_bev_efficienza}</span>",
        "Note BEV": "Efficienza Plug-to-Wheel ~75-80%",
        "FCEV (Idrogeno)": f"<span class='{class_fcev_efficienza}'>{sem_fcev_efficienza}</span>",
        "Note FCEV": "Efficienza Power-to-Wheel ~25-30%"
    }
]

df_matrix = pd.DataFrame(data_matrix)
st.write(df_matrix.to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 6. CONFRONTO ECONOMICO (CAPEX & OPEX)
# ---------------------------------------------------------
st.subheader("💰 Confronto Economico Stimato Anno")

capex_bev = num_veicoli * b["bev_costo_mezzo"]
capex_fcev = num_veicoli * b["fcev_costo_mezzo"]

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 🔋 Flotta BEV (Elettrico)")
    st.write(f"**CAPEX Mezzi:** € {capex_bev:,.2f}")
    st.write(f"**Consumo Annuo:** {kwh_anno:,.0f} kWh")
    st.write(f"**OPEX Energia Annuo:** € {costo_energia_bev_anno:,.2f}")

with col_b:
    st.markdown("### 💧 Flotta FCEV (Idrogeno)")
    st.write(f"**CAPEX Mezzi:** € {capex_fcev:,.2f}")
    st.write(f"**Consumo Annuo:** {kg_h2_anno:,.1f} kg H2")
    st.write(f"**OPEX Idrogeno Annuo:** € {costo_energia_fcev_anno:,.2f}")

# Raccomandazione Finale
st.markdown("---")
st.subheader("📌 Verdetto Strategico per il Comune / Azienda")

score_bev = [sem_bev_autonomia, sem_bev_tempo, sem_bev_infra, sem_bev_costokm, sem_bev_efficienza].count("🟢 Verde")
score_fcev = [sem_fcev_autonomia, sem_fcev_tempo, sem_fcev_infra, sem_fcev_costokm, sem_fcev_efficienza].count("🟢 Verde")

if score_bev > score_fcev:
    st.success(f"**Soluzione Consigliata: BEV (Elettrico)** — Ottiene un punteggio migliore in base alle percorrenze quotidiane ({km_giornalieri} km) e ai costi operativi attuali.")
elif score_fcev > score_bev:
    st.info(f"**Soluzione Consigliata: FCEV (Idrogeno)** — Ideale per soddisfare elevati requisiti di autonomia e tempi rapidi di rifornimento, a patto di disporre di infrastruttura dedicata.")
else:
    st.warning("**Soluzione Ibrida / Equivalente** — Entrambe le tecnologie presentano vantaggi e limiti specifici. Si consiglia un progetto pilota modulare.")
