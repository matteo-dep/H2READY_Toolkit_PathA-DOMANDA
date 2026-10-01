# -*- coding: utf-8 -*-
"""
H2READY - Tool 2.2 · testi dell'interfaccia in italiano, inglese e sloveno.

Sta in un file a parte perche' il 2.2 e' gia' lungo e il motore di calcolo si
legge meglio senza seicento righe di stringhe in mezzo.

CHIAVI DEI DATI, NON TRADOTTE
"tech", "catbase", "veicoli" e "oro" traducono solo l'ETICHETTA a schermo. Le
chiavi dei dizionari del tool ("Benzina", "Camion Pesante", "Montagna"...)
restano in italiano perche' le usa il motore di calcolo, e "T22_ESITO_PREVALENTE"
finisce cosi' com'e' nell'excelone: tradurle significherebbe spaccare sia i
confronti sia l'Action Plan.
"""

T = {

    # ======================================================================
    # ITALIANO
    # ======================================================================
    "it": {
        "title": "🚗 H2READY TOOLKIT - Tool 2.2: Simulatore Strategico di Flotta",
        "subtitle": "Confronto **Diesel / Elettrico / Idrogeno** con curve di proiezione "
                    "tecnologica (2024-2035) per un'analisi dinamica del TCO e delle "
                    "emissioni LCA.",
        "accesso": "Tool 2.2 - Simulatore Strategico di Flotta",
        "home": "⬅️ Torna al menu H2READY",
        "readme_exp": "ℹ️ Leggi istruzioni, logiche e assunzioni del simulatore",
        "readme_ko": "💡 Suggerimento: carica il file '{f}' nella stessa cartella per "
                     "vedere qui le istruzioni.",

        # --- sidebar ---
        "sb_missione": "1. Parametri di missione",
        "lbl_veicolo": "Tipo di veicolo",
        "lbl_km": "Percorrenza giornaliera (km)",
        "lbl_giorni": "Giorni operativi annui",
        "lbl_finestra": "Finestra massima per la ricarica (ore)",
        "help_finestra": "Ore in cui il mezzo è fermo e disponibile a ricaricare. "
                         "È il vincolo operativo che decide se un BEV è praticabile.",
        "sb_flotta": "2. Dimensionamento della flotta",
        "lbl_n": "Numero di veicoli da sostituire",
        "help_n": "Definisce la dimensione della flotta per fabbisogno energetico "
                  "totale e investimenti macro.",
        "sb_ambiente": "3. Condizioni ambientali",
        "lbl_oro": "Orografia del percorso",
        "lbl_inverno": "Clima invernale rigido (< 0 °C)",
        "help_inverno": "Penalizza soprattutto le batterie: consumano di più e "
                        "invecchiano più in fretta (lithium plating).",
        "sb_costi": "4. Costi energetici iniziali (2024)",
        "p_benzina": "Benzina (€/l)",
        "p_diesel": "Diesel (€/l)",
        "p_el_rete": "Elettricità di rete (€/kWh)",
        "p_el_fv": "Elettricità fotovoltaica (€/kWh)",
        "p_h2_rete": "H₂ da rete (€/kg)",
        "p_h2_fv": "H₂ autoprodotto (€/kg)",
        "p_pubblica": "Ricarica pubblica rapida (€/kWh)",
        "help_pubblica": "Usata solo per l'energia che non si riesce a caricare "
                         "al deposito.",
        "sb_proiezioni": "5. Proiezioni tecnologiche",
        "lbl_anno": "Anno previsto di acquisto",
        "lbl_vita": "Ciclo di vita utile (anni)",

        # --- verdetto ---
        "v_title": "📋 Verdetto di fattibilità operativa",
        "v_h2": "### 🔵 L'IDROGENO È LA SCELTA STRATEGICA MIGLIORE",
        "v_h2_txt": "L'elettrico non regge i vincoli fisici della missione: {m}. "
                    "L'idrogeno copre {km} km con un pieno da {min} minuti.",
        "v_mot_peso": "la batteria peserebbe {p} kg",
        "v_mot_tempo": "servirebbero {t} h di ricarica contro {d} h disponibili",
        "v_mot_aut": "il {q}% dell'energia andrebbe comprata a colonnina pubblica",
        "v_bev": "### 🟢 L'ELETTRICO (BEV) È FATTIBILE E PIÙ ECONOMICO",
        "v_bev_txt": "La batteria copre la missione da {km} km e si ricarica in {t} h, "
                     "dentro la finestra di {d} h. Costa € {e} in meno dell'idrogeno "
                     "sul ciclo di vita.",
        "v_both": "### 🔵 ENTRAMBE FATTIBILI: L'IDROGENO È PIÙ CONVENIENTE",
        "v_both_txt": "L'elettrico regge i vincoli fisici, ma sul ciclo di vita "
                      "l'idrogeno costa € {e} in meno.",
        "batt_ko": "⚠️ La batteria necessaria alla missione ({bt} kWh) supera il limite "
                   "di peso ammissibile ed è stata limitata a {bk} kWh. Con {a} km di "
                   "autonomia il mezzo **non completa i {km} km della giornata**: il "
                   "{q}% dell'energia va comprata a ricarica pubblica, con le soste "
                   "che comporta.",
        "batt_ok": "ℹ️ La batteria è stata limitata dal vincolo di peso ({bt} → {bk} kWh). "
                   "L'autonomia residua ({a} km) copre comunque la missione, ma senza il "
                   "margine di sicurezza del 33% previsto.",
        "lim_title": "### 🚦 Analisi dei limiti fisici dell'elettrico (BEV)",
        "m_peso": "Peso della batteria richiesta",
        "m_tempo": "Tempo di ricarica richiesto",
        "m_carico": "Carico utile perso",
        "m_delta": "Delta costo H₂ contro BEV",
        "d_tempo": "contro {d} h disponibili",
        "d_deroga": "netto deroga UE +2 t",
        "sostituzioni": "🔋 Nel ciclo di vita ({km} km) la batteria va sostituita **{n} "
                        "volta/e** (vita utile {v} km{f}): € {e} per veicolo, già inclusi "
                        "nel TCO.",
        "sost_freddo": ", ridotta dal clima rigido",

        # --- gap ---
        "g_title": "💰 Strategia incentivi e gap analysis",
        "g_sub": "Confronto rispetto al veicolo **{f}** per l'intero ciclo di vita "
                 "({km} km, {a} anni).",
        "g_bev": "🔋 Elettrico ({n})",
        "g_h2": "💧 Idrogeno ({n})",
        "g_tot": "Gap TCO totale",
        "g_km": "Gap al chilometro",
        "g_flotta": "Gap sull'intera flotta",

        # --- grafici ---
        "c_title": "📊 Analisi dei valori assoluti (TCO e LCA)",
        "c_a": "A. Autonomia massima [km]",
        "c_b": "B. Consumo [kWh/km]",
        "c_c": "C. Efficienza globale WtW [%]",
        "c_d": "D. Emissioni LCA totali [t CO₂]",
        "c_rendimento": "Rendimento %",
        "c_fase": "Fase",
        "c_costruzione": "Costruzione",
        "c_uso": "Carburante / uso",
        "c_e": "E. Costo totale di proprietà (TCO) spacchettato [€]",
        "c_voce": "Voce",
        "c_capex": "Acquisto del mezzo (CAPEX)",
        "c_maint": "Manutenzione (OPEX)",
        "c_fuel": "Carburante (OPEX)",
        "c_batt": "Sostituzione della batteria",
        "c_euro": "Euro (€) nel ciclo di vita",
        "c_baseline": "Riferimento {f}",
        "payload": "📦 **Attenzione al carico utile.** Il mezzo elettrico perde {b} t di "
                   "portata e l'idrogeno {h} t (fonte: Roland Berger, già al netto della "
                   "deroga UE). Sul costo per tonnellata trasportata il confronto cambia: ",

        # --- macro ---
        "mm_title": "🏢 Analisi macro: transizione dell'intera flotta ({n} veicoli)",
        "mm_sub": "Aggregazione del fabbisogno energetico e dei costi annui. Evidenzia "
                  "la differenza fra caricare le batterie dalla rete e produrre idrogeno "
                  "verde con elettrolizzatori (efficienza: circa 55 kWh per kg di H₂).",
        "mm_bev": "🔋 Scenario 100% BEV",
        "mm_h2": "💧 Scenario 100% idrogeno",
        "mm_el": "Fabbisogno elettrico diretto",
        "mm_el_d": "Energia per la ricarica delle batterie",
        "mm_capex": "CAPEX veicoli (investimento)",
        "mm_opex": "OPEX annuo (energia e manutenzione)",
        "mm_massa": "Massa di H₂ consumata",
        "mm_el_h2": "Fabbisogno elettrico per l'H₂ (FER)",
        "mm_diff": "Differenza WtW contro BEV: +{v} MWh",
        "mm_infra": """
**💡 Attenzione agli oneri infrastrutturali non inclusi (ricarica / rifornimento):**
Ai costi dei mezzi va sempre sommata la costruzione dell'infrastruttura.
* **BEV:** da circa € 2.000 (wallbox lente) a oltre € 80.000 per ogni colonnina fast o ultra-fast dedicata ai mezzi pesanti.
* **H2 (FCEV):** una HRS ad alta pressione richiede un CAPEX fra **1 e oltre 3 milioni di €** in funzione dei kg erogati al giorno (vedi Tool 2.8).
""",

        # --- tabella ---
        "tab_title": "📋 Tabella dati completa",
        "tab_tec": "Tecnologia",
        "tab_aut": "Autonomia [km]",
        "tab_cons": "Consumo [kWh/km]",
        "tab_eta": "Efficienza WtW [%]",
        "tab_tco": "TCO ciclo di vita [€]",
        "tab_eurkm": "€/km",
        "tab_eurtkm": "€/t·km",
        "tab_pay": "Carico utile [t]",

        # --- export ---
        "e_title": "💾 Esportazione",
        "e_assoc": "I dati verranno associati a {c} (ID {id}).",
        "e_btn": "💾 Esporta nel database centrale",
        "e_ok": "✅ Dati trasmessi correttamente al database centrale.",
        "e_resp": "Risposta del server: {r}",
        "e_err": "Errore di sincronizzazione (codice {c})",
        "e_timeout": "⏳ Il server non ha risposto in tempo. Quasi sempre significa che i "
                     "dati sono stati scritti: controlla il foglio prima di ripetere l'invio.",
        "e_conn": "Errore di connessione: {e}",

        # --- etichette delle chiavi di dato ---
        "veicoli": {"Automobile": "Automobile", "Camion Pesante": "Camion pesante",
                    "Autobus Urbano": "Autobus urbano",
                    "Autobus Extraurbano": "Autobus extraurbano"},
        "oro": {"Pianura": "Pianura", "Collinare": "Collinare", "Montagna": "Montagna"},
        "tech": {"Benzina": "Benzina", "Diesel": "Diesel",
                 "Elettrico rete": "Elettrico da rete",
                 "Elettrico autoprodotto": "Elettrico autoprodotto",
                 "Idrogeno rete": "Idrogeno da rete",
                 "Idrogeno autoprodotto": "Idrogeno autoprodotto"},
        "catbase": {"Elettrico (BEV)": "Elettrico (BEV)",
                    "Idrogeno (FCEV)": "Idrogeno (FCEV)"},
    },

    # ======================================================================
    # ENGLISH
    # ======================================================================
    "en": {
        "title": "🚗 H2READY TOOLKIT - Tool 2.2: Strategic Fleet Simulator",
        "subtitle": "**Diesel / Electric / Hydrogen** compared, with technology "
                    "projection curves (2024-2035) for a dynamic analysis of TCO and "
                    "LCA emissions.",
        "accesso": "Tool 2.2 - Strategic Fleet Simulator",
        "home": "⬅️ Back to the H2READY menu",
        "readme_exp": "ℹ️ Read the simulator's instructions, logic and assumptions",
        "readme_ko": "💡 Tip: place the file '{f}' in the same folder to see the "
                     "instructions here.",

        "sb_missione": "1. Mission parameters",
        "lbl_veicolo": "Vehicle type",
        "lbl_km": "Daily distance (km)",
        "lbl_giorni": "Operating days per year",
        "lbl_finestra": "Maximum charging window (hours)",
        "help_finestra": "Hours when the vehicle is idle and available to charge. "
                         "It is the operational constraint that decides whether a BEV "
                         "is viable.",
        "sb_flotta": "2. Fleet sizing",
        "lbl_n": "Number of vehicles to replace",
        "help_n": "Sets the fleet size for total energy demand and macro investment.",
        "sb_ambiente": "3. Environmental conditions",
        "lbl_oro": "Route terrain",
        "lbl_inverno": "Harsh winter climate (< 0 °C)",
        "help_inverno": "Penalises batteries above all: they consume more and age "
                        "faster (lithium plating).",
        "sb_costi": "4. Initial energy costs (2024)",
        "p_benzina": "Petrol (€/l)",
        "p_diesel": "Diesel (€/l)",
        "p_el_rete": "Grid electricity (€/kWh)",
        "p_el_fv": "PV electricity (€/kWh)",
        "p_h2_rete": "Grid H₂ (€/kg)",
        "p_h2_fv": "Self-produced H₂ (€/kg)",
        "p_pubblica": "Public fast charging (€/kWh)",
        "help_pubblica": "Used only for the energy that cannot be charged at the depot.",
        "sb_proiezioni": "5. Technology projections",
        "lbl_anno": "Expected year of purchase",
        "lbl_vita": "Service life (years)",

        "v_title": "📋 Operational feasibility verdict",
        "v_h2": "### 🔵 HYDROGEN IS THE BETTER STRATEGIC CHOICE",
        "v_h2_txt": "Electric does not meet the physical constraints of the mission: "
                    "{m}. Hydrogen covers {km} km on a {min}-minute refuelling stop.",
        "v_mot_peso": "the battery would weigh {p} kg",
        "v_mot_tempo": "it would take {t} h of charging against {d} h available",
        "v_mot_aut": "{q}% of the energy would have to be bought at public chargers",
        "v_bev": "### 🟢 ELECTRIC (BEV) IS FEASIBLE AND CHEAPER",
        "v_bev_txt": "The battery covers the {km} km mission and recharges in {t} h, "
                     "within the {d} h window. It costs € {e} less than hydrogen over "
                     "the life cycle.",
        "v_both": "### 🔵 BOTH FEASIBLE: HYDROGEN IS CHEAPER",
        "v_both_txt": "Electric meets the physical constraints, but over the life cycle "
                      "hydrogen costs € {e} less.",
        "batt_ko": "⚠️ The battery the mission requires ({bt} kWh) exceeds the admissible "
                   "weight limit and has been capped at {bk} kWh. With {a} km of range "
                   "the vehicle **does not complete the {km} km of the day**: {q}% of the "
                   "energy must be bought at public chargers, with the stops that implies.",
        "batt_ok": "ℹ️ The battery was capped by the weight constraint ({bt} → {bk} kWh). "
                   "The remaining range ({a} km) still covers the mission, but without the "
                   "33% safety margin assumed.",
        "lim_title": "### 🚦 Physical limits of the electric option (BEV)",
        "m_peso": "Required battery weight",
        "m_tempo": "Required charging time",
        "m_carico": "Payload lost",
        "m_delta": "H₂ versus BEV cost delta",
        "d_tempo": "against {d} h available",
        "d_deroga": "net of the EU +2 t derogation",
        "sostituzioni": "🔋 Over the life cycle ({km} km) the battery must be replaced "
                        "**{n} time(s)** (service life {v} km{f}): € {e} per vehicle, "
                        "already included in the TCO.",
        "sost_freddo": ", shortened by the harsh climate",

        "g_title": "💰 Incentive strategy and gap analysis",
        "g_sub": "Compared against the **{f}** vehicle over the whole life cycle "
                 "({km} km, {a} years).",
        "g_bev": "🔋 Electric ({n})",
        "g_h2": "💧 Hydrogen ({n})",
        "g_tot": "Total TCO gap",
        "g_km": "Gap per kilometre",
        "g_flotta": "Gap across the whole fleet",

        "c_title": "📊 Absolute values (TCO and LCA)",
        "c_a": "A. Maximum range [km]",
        "c_b": "B. Consumption [kWh/km]",
        "c_c": "C. Overall WtW efficiency [%]",
        "c_d": "D. Total LCA emissions [t CO₂]",
        "c_rendimento": "Efficiency %",
        "c_fase": "Phase",
        "c_costruzione": "Manufacturing",
        "c_uso": "Fuel / use",
        "c_e": "E. Total cost of ownership (TCO), broken down [€]",
        "c_voce": "Item",
        "c_capex": "Vehicle purchase (CAPEX)",
        "c_maint": "Maintenance (OPEX)",
        "c_fuel": "Fuel (OPEX)",
        "c_batt": "Battery replacement",
        "c_euro": "Euro (€) over the life cycle",
        "c_baseline": "Baseline {f}",
        "payload": "📦 **Mind the payload.** The electric vehicle loses {b} t of capacity "
                   "and hydrogen {h} t (source: Roland Berger, already net of the EU "
                   "derogation). Per tonne carried the comparison changes: ",

        "mm_title": "🏢 Macro analysis: converting the whole fleet ({n} vehicles)",
        "mm_sub": "Aggregated energy demand and annual costs. It shows the difference "
                  "between charging batteries from the grid and producing green hydrogen "
                  "with electrolysers (efficiency: about 55 kWh per kg of H₂).",
        "mm_bev": "🔋 100% BEV scenario",
        "mm_h2": "💧 100% hydrogen scenario",
        "mm_el": "Direct electricity demand",
        "mm_el_d": "Energy for battery charging",
        "mm_capex": "Vehicle CAPEX (investment)",
        "mm_opex": "Annual OPEX (energy and maintenance)",
        "mm_massa": "Mass of H₂ consumed",
        "mm_el_h2": "Electricity demand for H₂ (renewable)",
        "mm_diff": "WtW difference against BEV: +{v} MWh",
        "mm_infra": """
**💡 Mind the infrastructure costs, which are not included (charging / refuelling):**
The cost of building the infrastructure must always be added to the vehicles.
* **BEV:** from about € 2,000 (slow wallbox) to over € 80,000 for each fast or ultra-fast charger dedicated to heavy vehicles.
* **H2 (FCEV):** a high-pressure HRS requires a CAPEX between **€ 1 million and over € 3 million** depending on the kg dispensed per day (see Tool 2.8).
""",

        "tab_title": "📋 Full data table",
        "tab_tec": "Technology",
        "tab_aut": "Range [km]",
        "tab_cons": "Consumption [kWh/km]",
        "tab_eta": "WtW efficiency [%]",
        "tab_tco": "Life-cycle TCO [€]",
        "tab_eurkm": "€/km",
        "tab_eurtkm": "€/t·km",
        "tab_pay": "Payload [t]",

        "e_title": "💾 Export",
        "e_assoc": "The data will be linked to {c} (ID {id}).",
        "e_btn": "💾 Export to the central database",
        "e_ok": "✅ Data successfully transmitted to the central database.",
        "e_resp": "Server response: {r}",
        "e_err": "Synchronisation error (code {c})",
        "e_timeout": "⏳ The server did not answer in time. This almost always means the "
                     "data was written: check the sheet before sending again.",
        "e_conn": "Connection error: {e}",

        "veicoli": {"Automobile": "Car", "Camion Pesante": "Heavy truck",
                    "Autobus Urbano": "Urban bus",
                    "Autobus Extraurbano": "Intercity bus"},
        "oro": {"Pianura": "Flat", "Collinare": "Hilly", "Montagna": "Mountain"},
        "tech": {"Benzina": "Petrol", "Diesel": "Diesel",
                 "Elettrico rete": "Electric, grid",
                 "Elettrico autoprodotto": "Electric, self-produced",
                 "Idrogeno rete": "Hydrogen, grid",
                 "Idrogeno autoprodotto": "Hydrogen, self-produced"},
        "catbase": {"Elettrico (BEV)": "Electric (BEV)",
                    "Idrogeno (FCEV)": "Hydrogen (FCEV)"},
    },

    # ======================================================================
    # SLOVENŠČINA
    # ======================================================================
    "sl": {
        "title": "🚗 H2READY TOOLKIT - Orodje 2.2: Strateški simulator voznega parka",
        "subtitle": "Primerjava **dizel / elektrika / vodik** s krivuljami tehnološkega "
                    "razvoja (2024-2035) za dinamično analizo TCO in emisij LCA.",
        "accesso": "Orodje 2.2 - Strateški simulator voznega parka",
        "home": "⬅️ Nazaj na meni H2READY",
        "readme_exp": "ℹ️ Preberite navodila, logiko in predpostavke simulatorja",
        "readme_ko": "💡 Nasvet: datoteko '{f}' dodajte v isto mapo, da se navodila "
                     "prikažejo tukaj.",

        "sb_missione": "1. Parametri naloge",
        "lbl_veicolo": "Vrsta vozila",
        "lbl_km": "Dnevna razdalja (km)",
        "lbl_giorni": "Število obratovalnih dni na leto",
        "lbl_finestra": "Največje okno za polnjenje (ure)",
        "help_finestra": "Ure, ko vozilo miruje in se lahko polni. To je operativna "
                         "omejitev, ki odloči, ali je baterijsko vozilo izvedljivo.",
        "sb_flotta": "2. Dimenzioniranje voznega parka",
        "lbl_n": "Število vozil za zamenjavo",
        "help_n": "Določa velikost voznega parka za skupne energetske potrebe in "
                  "naložbe na ravni občine.",
        "sb_ambiente": "3. Okoljske razmere",
        "lbl_oro": "Razgibanost trase",
        "lbl_inverno": "Ostra zima (< 0 °C)",
        "help_inverno": "Najbolj prizadene baterije: porabijo več in se hitreje "
                        "starajo (lithium plating).",
        "sb_costi": "4. Izhodiščni stroški energije (2024)",
        "p_benzina": "Bencin (€/l)",
        "p_diesel": "Dizel (€/l)",
        "p_el_rete": "Omrežna elektrika (€/kWh)",
        "p_el_fv": "Fotovoltaična elektrika (€/kWh)",
        "p_h2_rete": "Omrežni H₂ (€/kg)",
        "p_h2_fv": "Lastni H₂ (€/kg)",
        "p_pubblica": "Javno hitro polnjenje (€/kWh)",
        "help_pubblica": "Uporablja se le za energijo, ki je ni mogoče napolniti "
                         "v depoju.",
        "sb_proiezioni": "5. Tehnološke projekcije",
        "lbl_anno": "Predvideno leto nakupa",
        "lbl_vita": "Življenjska doba (leta)",

        "v_title": "📋 Sodba o operativni izvedljivosti",
        "v_h2": "### 🔵 VODIK JE BOLJŠA STRATEŠKA IZBIRA",
        "v_h2_txt": "Elektrika ne vzdrži fizičnih omejitev naloge: {m}. Vodik pokrije "
                    "{km} km s polnjenjem, ki traja {min} minut.",
        "v_mot_peso": "baterija bi tehtala {p} kg",
        "v_mot_tempo": "potrebnih bi bilo {t} h polnjenja proti {d} h, ki so na voljo",
        "v_mot_aut": "{q} % energije bi bilo treba kupiti na javnih polnilnicah",
        "v_bev": "### 🟢 ELEKTRIČNO (BEV) JE IZVEDLJIVO IN CENEJŠE",
        "v_bev_txt": "Baterija pokrije nalogo {km} km in se napolni v {t} h, znotraj "
                     "okna {d} h. V življenjski dobi stane € {e} manj kot vodik.",
        "v_both": "### 🔵 OBOJE IZVEDLJIVO: VODIK JE CENEJŠI",
        "v_both_txt": "Elektrika vzdrži fizične omejitve, vendar v življenjski dobi "
                      "vodik stane € {e} manj.",
        "batt_ko": "⚠️ Baterija, ki jo naloga zahteva ({bt} kWh), presega dopustno težo "
                   "in je bila omejena na {bk} kWh. Z dosegom {a} km vozilo **ne opravi "
                   "{km} km dnevne naloge**: {q} % energije je treba kupiti na javnih "
                   "polnilnicah, z vsemi postanki, ki jih to prinese.",
        "batt_ok": "ℹ️ Baterijo je omejila teža ({bt} → {bk} kWh). Preostali doseg "
                   "({a} km) nalogo še pokrije, vendar brez predvidenih 33 % varnostne "
                   "rezerve.",
        "lim_title": "### 🚦 Fizične omejitve električne rešitve (BEV)",
        "m_peso": "Potrebna teža baterije",
        "m_tempo": "Potreben čas polnjenja",
        "m_carico": "Izgubljena nosilnost",
        "m_delta": "Razlika v stroških H₂ proti BEV",
        "d_tempo": "proti {d} h, ki so na voljo",
        "d_deroga": "brez odstopanja EU +2 t",
        "sostituzioni": "🔋 V življenjski dobi ({km} km) je treba baterijo zamenjati "
                        "**{n}-krat** (življenjska doba {v} km{f}): € {e} na vozilo, "
                        "že vključeno v TCO.",
        "sost_freddo": ", skrajšana zaradi ostrega podnebja",

        "g_title": "💰 Strategija spodbud in analiza vrzeli",
        "g_sub": "Primerjava z vozilom **{f}** za celotno življenjsko dobo "
                 "({km} km, {a} let).",
        "g_bev": "🔋 Električno ({n})",
        "g_h2": "💧 Vodik ({n})",
        "g_tot": "Skupna vrzel TCO",
        "g_km": "Vrzel na kilometer",
        "g_flotta": "Vrzel za celoten vozni park",

        "c_title": "📊 Analiza absolutnih vrednosti (TCO in LCA)",
        "c_a": "A. Največji doseg [km]",
        "c_b": "B. Poraba [kWh/km]",
        "c_c": "C. Skupna učinkovitost WtW [%]",
        "c_d": "D. Skupne emisije LCA [t CO₂]",
        "c_rendimento": "Učinkovitost %",
        "c_fase": "Faza",
        "c_costruzione": "Izdelava",
        "c_uso": "Gorivo / uporaba",
        "c_e": "E. Skupni stroški lastništva (TCO) po postavkah [€]",
        "c_voce": "Postavka",
        "c_capex": "Nakup vozila (CAPEX)",
        "c_maint": "Vzdrževanje (OPEX)",
        "c_fuel": "Gorivo (OPEX)",
        "c_batt": "Zamenjava baterije",
        "c_euro": "Evri (€) v življenjski dobi",
        "c_baseline": "Izhodišče {f}",
        "payload": "📦 **Pozor na nosilnost.** Električno vozilo izgubi {b} t nosilnosti, "
                   "vodikovo pa {h} t (vir: Roland Berger, že brez odstopanja EU). Na "
                   "prepeljano tono se primerjava spremeni: ",

        "mm_title": "🏢 Makro analiza: pretvorba celotnega voznega parka ({n} vozil)",
        "mm_sub": "Združene energetske potrebe in letni stroški. Pokaže razliko med "
                  "polnjenjem baterij iz omrežja in proizvodnjo zelenega vodika z "
                  "elektrolizerji (učinkovitost: približno 55 kWh na kg H₂).",
        "mm_bev": "🔋 Scenarij 100 % BEV",
        "mm_h2": "💧 Scenarij 100 % vodik",
        "mm_el": "Neposredne potrebe po elektriki",
        "mm_el_d": "Energija za polnjenje baterij",
        "mm_capex": "CAPEX vozil (naložba)",
        "mm_opex": "Letni OPEX (energija in vzdrževanje)",
        "mm_massa": "Masa porabljenega H₂",
        "mm_el_h2": "Potrebe po elektriki za H₂ (OVE)",
        "mm_diff": "Razlika WtW proti BEV: +{v} MWh",
        "mm_infra": """
**💡 Pozor na infrastrukturne stroške, ki niso vključeni (polnjenje / oskrba):**
Stroškom vozil je treba vedno prišteti gradnjo infrastrukture.
* **BEV:** od približno 2.000 € (počasna stenska polnilnica) do več kot 80.000 € za vsako hitro ali ultrahitro polnilnico za težka vozila.
* **H2 (FCEV):** visokotlačna polnilnica HRS zahteva CAPEX med **1 in več kot 3 milijoni €**, odvisno od dnevno oddanih kilogramov (glej orodje 2.8).
""",

        "tab_title": "📋 Celotna tabela podatkov",
        "tab_tec": "Tehnologija",
        "tab_aut": "Doseg [km]",
        "tab_cons": "Poraba [kWh/km]",
        "tab_eta": "Učinkovitost WtW [%]",
        "tab_tco": "TCO v življenjski dobi [€]",
        "tab_eurkm": "€/km",
        "tab_eurtkm": "€/t·km",
        "tab_pay": "Nosilnost [t]",

        "e_title": "💾 Izvoz",
        "e_assoc": "Podatki bodo povezani z {c} (ID {id}).",
        "e_btn": "💾 Izvozi v osrednjo bazo",
        "e_ok": "✅ Podatki uspešno poslani v osrednjo bazo.",
        "e_resp": "Odgovor strežnika: {r}",
        "e_err": "Napaka sinhronizacije (koda {c})",
        "e_timeout": "⏳ Strežnik ni odgovoril pravočasno. Skoraj vedno to pomeni, da so "
                     "podatki zapisani: preverite preglednico, preden znova pošljete.",
        "e_conn": "Napaka povezave: {e}",

        "veicoli": {"Automobile": "Osebno vozilo", "Camion Pesante": "Težko tovorno vozilo",
                    "Autobus Urbano": "Mestni avtobus",
                    "Autobus Extraurbano": "Medkrajevni avtobus"},
        "oro": {"Pianura": "Ravnina", "Collinare": "Gričevje", "Montagna": "Gorato"},
        "tech": {"Benzina": "Bencin", "Diesel": "Dizel",
                 "Elettrico rete": "Električno iz omrežja",
                 "Elettrico autoprodotto": "Električno, lastna proizvodnja",
                 "Idrogeno rete": "Vodik iz omrežja",
                 "Idrogeno autoprodotto": "Vodik, lastna proizvodnja"},
        "catbase": {"Elettrico (BEV)": "Električno (BEV)",
                    "Idrogeno (FCEV)": "Vodik (FCEV)"},
    },
}
