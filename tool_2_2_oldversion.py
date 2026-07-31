import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tool 2.2 - TCO Flotte & Trasporti", layout="wide")

st.title("🚘 Tool 2.2 – Calcolatore TCO & Confronto Flotte")
st.caption("Confronto Tecnico-Economico: Diesel vs Elettrico (BEV) vs Idrogeno (FCHV)")

# ==========================================
# 1. BARRA LATERALE: INPUT PARAMETRI
# ==========================================
st.sidebar.header("⚙️ Parametri della Flotta")
tipo_mezzo = st.sidebar.selectbox(
    "Tipologia Mezzo", 
    ["Auto Aziendali / Leggeri", "Furgoni LCV (<3.5t)", "Autobus TPL", "Camion Pesanti / Camion Cava"]
)
num_mezzi = st.sidebar.number_input("Numero veicoli in flotta", min_value=1, value=5)
km_anno_mezzo = st.sidebar.number_input("Percorrenza annua per singolo mezzo (km/anno)", min_value=1000, value=25000)

st.sidebar.markdown("---")
st.sidebar.header("🏔️ Condizioni di Esercizio")
condizioni = st.sidebar.selectbox(
    "Orografia e Clima",
    ["Standard (Pianura / Misto)", "Gravose (Montagna / Clima Rigido)"]
)

st.sidebar.markdown("---")
st.sidebar.header("💶 Costo Vettori Energetici")
costo_diesel = st.sidebar.number_input("Costo Diesel (€/litro)", value=1.75)
costo_kwh = st.sidebar.number_input("Costo Elettricità (€/kWh)", value=0.28)
costo_h2 = st.sidebar.number_input("Costo Idrogeno (€/kg)", value=11.00)

# ==========================================
# 2. MOTORE DI CALCOLO E FISICA DEI CONSUMI
# ==========================================
tot_km_flotta = num_mezzi * km_anno_mezzo

# Consumi Base
if "Auto" in tipo_mezzo:
    cons_diesel = 0.06  # litri/km
    cons_bev = 0.18     # kWh/km
    cons_h2 = 0.009     # kg/km
elif "Furgoni" in tipo_mezzo:
    cons_diesel = 0.09
    cons_bev = 0.28
    cons_h2 = 0.015
else:  # Mezzi Pesanti / Bus
    cons_diesel = 0.32
    cons_bev = 1.20
    cons_h2 = 0.080

# Moltiplicatori per orografia e clima (selezionati dall'utente)
if condizioni == "Gravose (Montagna / Clima Rigido)":
    st.info("⚠️ **Condizioni Gravose attivate:** I mezzi elettrici (BEV) subiscono una forte penalità a causa del riscaldamento della cabina in inverno che drena le batterie.")
    cons_diesel = cons_diesel * 1.10  # +10% 
    cons_bev = cons_bev * 1.30        # +30% (Batterie soffrono il freddo + riscaldamento)
    cons_h2 = cons_h2 * 1.10          # +10% (La Fuel Cell usa il suo calore di scarto per la cabina)

# Spesa Totale Annuo
spesa_diesel = tot_km_flotta * cons_diesel * costo_diesel
spesa_bev = tot_km_flotta * cons_bev * costo_kwh
spesa_h2 = tot_km_flotta * cons_h2 * costo_h2

# ==========================================
# 3. OUTPUT E METRICHE
# ==========================================
st.subheader(f"📊 Risultati per {num_mezzi} veicoli ({tipo_mezzo}) — {tot_km_flotta:,} km/anno complessivi")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⛽ Diesel Tradizionale", f"€ {spesa_diesel:,.2f} /anno")
    st.caption(f"Consumo: {tot_km_flotta * cons_diesel:,.0f} Litri")
with col2:
    st.metric("⚡ Elettrico Batteria (BEV)", f"€ {spesa_bev:,.2f} /anno")
    st.caption(f"Consumo: {tot_km_flotta * cons_bev:,.0f} kWh")
with col3:
    st.metric("🟢 Idrogeno Fuel Cell (FCHV)", f"€ {spesa_h2:,.2f} /anno")
    st.caption(f"Consumo: {tot_km_flotta * cons_h2:,.0f} kg H₂")

# ==========================================
# 4. VALUTAZIONE A SEMAFORI 🚦
# ==========================================
st.markdown("---")
st.header("🚦 Valutazione di Sostenibilità e Fattibilità Operativa")

# Logica Dinamica per i Semafori
if "Auto" in tipo_mezzo or "Furgoni" in tipo_mezzo:
    if condizioni == "Standard (Pianura / Misto)":
        st.success("🟢 **ELETTRICO (BEV) - SCELTA OTTIMALE:** Per i mezzi leggeri in percorsi standard, l'elettrico a batteria offre il TCO (Costo Totale) più basso e la logistica di ricarica più semplice.")
        st.warning("🟡 **IDROGENO (FCHV) - DA VALUTARE:** Tecnologicamente perfetto, ma il costo della molecola non giustifica l'investimento per flotte leggere a corto raggio.")
    else:
        st.success("🟢 **ELETTRICO (BEV) - SCELTA CONSIGLIATA:** Rimane l'opzione più economica, a patto di prevedere un calo di autonomia invernale del 30% e pianificare le ricariche.")
        st.warning("🟡 **IDROGENO (FCHV) - BUONA ALTERNATIVA:** L'idrogeno garantisce che il furgone mantenga la sua autonomia completa anche sotto zero, utile se le tratte sono molto lunghe.")
else:
    # Logica per Autobus e Camion Pesanti
    if condizioni == "Gravose (Montagna / Clima Rigido)":
        st.success("🟢 **IDROGENO (FCHV) - SCELTA STRATEGICA OTTIMALE:** Il freddo e le pendenze penalizzano troppo i camion/bus a batteria. L'idrogeno garantisce autonomia, tempi di ricarica rapidi e non sacrifica il carico utile del rimorchio.")
        st.error("🔴 **ELETTRICO (BEV) - RISCHIO OPERATIVO:** Il peso immenso delle batterie riduce i passeggeri/merci trasportabili. Inoltre, il riscaldamento invernale della grande cabina drena drasticamente l'autonomia.")
    else:
        st.warning("🟡 **IDROGENO (FCHV) - COMPETITIVO:** Ottimo per lunghe tratte e uso 24/7. La convenienza finale dipenderà dal costo di approvvigionamento dell'H2 (target < 7 €/kg).")
        st.warning("🟡 **ELETTRICO (BEV) - FATTIBILE:** Ottimo per i bus urbani e la logistica a corto raggio di pianura dove si può ricaricare di notte in deposito.")

# Il Diesel prende sempre semaforo rosso per policy ambientale (contesto H2Ready)
st.error("🔴 **DIESEL TRADIZIONALE - OBSOLESCENZA:** Sebbene i costi vivi possano apparire ancora bassi, è una tecnologia in via di dismissione a causa delle direttive UE, vincoli ESG e divieti di accesso ai centri urbani.")
