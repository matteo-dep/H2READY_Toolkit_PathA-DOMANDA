"""
H2READY - 1.3 Il tuo percorso / Your pathway / Vasa pot

Pagina di smistamento dopo il questionario 1.2.

E' l'unico indirizzo da distribuire insieme al 1.1: mostra quali percorsi si
sono aperti, quali strumenti compilare e a che punto e' il lavoro.

LINGUA
La pagina e' trilingue. La lingua si sceglie in tre modi, in questo ordine:
  1. query string  ?lang=sl   -> cosi' si puo' distribuire ai Comuni sloveni
                                 un indirizzo che apre gia' la pagina giusta
  2. selettore nella barra laterale
  3. italiano, come ripiego
La scelta viaggia poi verso i tool successivi dentro l'URL, insieme all'ID.
"""

import streamlit as st

import h2ready as H

st.set_page_config(page_title="H2READY TOOLKIT: Tool 1.3", page_icon="🧭",
                   layout="centered")

# ---------------------------------------------------------------------------
# LINGUA
# ---------------------------------------------------------------------------
ETICHETTE = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
CODICI = {v: k for k, v in ETICHETTE.items()}

da_url = ""
try:
    da_url = str(st.query_params.get("lang", "")).strip().lower()
except Exception:
    da_url = ""

# La query string vale una volta sola: dopo, comanda il selettore, altrimenti
# l'utente non riuscirebbe piu' a cambiare lingua su un indirizzo con ?lang=.
if da_url in CODICI and not st.session_state.get("h2ready_lang_da_url"):
    H.imposta_lingua(da_url)
    st.session_state["h2ready_lang_da_url"] = True

iniziale = H.lingua_corrente()
scelta = st.sidebar.selectbox(
    "🌐 Lingua / Language / Jezik",
    list(ETICHETTE.keys()),
    index=list(ETICHETTE.values()).index(iniziale) if iniziale in ETICHETTE.values() else 0,
)
LANG = ETICHETTE[scelta]
H.imposta_lingua(LANG)

# ---------------------------------------------------------------------------
# TESTI PROPRI DELLA PAGINA
# Quelli condivisi con gli altri tool stanno in h2ready.TESTI e si leggono con
# H.TT(). Qui restano solo le stringhe che esistono unicamente in questa pagina.
# ---------------------------------------------------------------------------
P = {
    "sottotitolo": {
        "it": "Tool 1.3: Il percorso del tuo Comune",
        "en": "Tool 1.3: Your municipality's pathway",
        "sl": "Orodje 1.3: Pot vaše občine",
    },
    "titolo_accesso": {
        "it": "Tool 1.3 - Il tuo percorso",
        "en": "Tool 1.3 - Your pathway",
        "sl": "Orodje 1.3 - Vaša pot",
    },
    "a_che_punto": {
        "it": "A che punto sei",
        "en": "Where you stand",
        "sl": "Kje ste",
    },
    "i_tuoi_percorsi": {
        "it": "I tuoi percorsi",
        "en": "Your pathways",
        "sl": "Vaše poti",
    },
    "strumenti": {
        "it": "Strumenti da compilare",
        "en": "Tools to complete",
        "sl": "Orodja za izpolniti",
    },
    "ap_sezione": {
        "it": "Il passo finale",
        "en": "The final step",
        "sl": "Zadnji korak",
    },
    "ap_spiega": {
        "it": "Quando gli strumenti sono compilati, il generatore mette insieme tutto "
              "in un unico documento — PDF e Word — da usare come base per un atto di "
              "indirizzo, come allegato a una candidatura o come documento di confronto "
              "con gli stakeholder.",
        "en": "Once the tools are filled in, the generator assembles everything into a "
              "single document — PDF and Word — to use as the basis for a council "
              "resolution, as an annex to a funding application, or as a document to "
              "discuss with stakeholders.",
        "sl": "Ko so orodja izpolnjena, generator vse združi v en dokument — PDF in Word "
              "— ki ga lahko uporabite kot podlago za občinski sklep, kot prilogo k "
              "vlogi za sredstva ali kot dokument za razpravo z deležniki.",
    },
    "punteggio": {"it": "punteggio", "en": "score", "sl": "ocena"},
    "nessun_percorso": {
        "it": "Nessun percorso risulta attivo. Verifica di aver completato il "
              "questionario 1.2: se i punteggi ci sono e restano sotto soglia, "
              "l'idrogeno non è la priorità per questo territorio, e conviene "
              "concentrarsi su elettrificazione ed efficienza energetica.",
        "en": "No pathway is active. Check that questionnaire 1.2 has been "
              "completed: if the scores are there and stay below threshold, "
              "hydrogen is not the priority for this territory, and the effort "
              "is better spent on electrification and energy efficiency.",
        "sl": "Nobena pot ni aktivna. Preverite, ali je vprašalnik 1.2 izpolnjen: "
              "če ocene obstajajo in ostajajo pod pragom, vodik za to območje ni "
              "prednostna naloga, zato je bolje vlagati v elektrifikacijo in "
              "energetsko učinkovitost.",
    },
    "nota_richiesta": {
        "it": "Per {cosa} l'accesso avviene su richiesta al gruppo di progetto: "
              "scrivi a {contatto} indicando il codice del Comune.",
        "en": "For {cosa}, access is granted on request to the project team: "
              "write to {contatto} quoting your municipality code.",
        "sl": "Za {cosa} je dostop mogoč na zahtevo pri projektni skupini: "
              "pišite na {contatto} in navedite kodo občine.",
    },
    "nota_avanzati": {
        "it": "gli strumenti di dimensionamento (2.6 e 2.8)",
        "en": "the sizing tools (2.6 and 2.8)",
        "sl": "orodja za dimenzioniranje (2.6 in 2.8)",
    },
    "nota_fast": {
        "it": "gli strumenti H2 FAST",
        "en": "the H2 FAST tools",
        "sl": "orodja H2 FAST",
    },
    "e_cong": {"it": " e ", "en": " and ", "sl": " in "},
}


def T(chiave, **valori):
    testo = P[chiave].get(LANG) or P[chiave]["it"]
    return testo.format(**valori) if valori else testo


# ---------------------------------------------------------------------------
# PAGINA
# ---------------------------------------------------------------------------
st.markdown(
    '<div style="background:linear-gradient(90deg,#003399,#0057c2);padding:20px;'
    'border-radius:12px;text-align:center">'
    '<h2 style="color:white;margin:0;letter-spacing:1px">H2READY TOOLKIT</h2>'
    f'<p style="color:#cddafc;margin:4px 0 0">{T("sottotitolo")}</p></div>',
    unsafe_allow_html=True)
st.write("")

comune = H.blocco_accesso(T("titolo_accesso"), lingua=LANG)
if comune is None:
    st.stop()

liv = H.livello(comune)
H.intestazione_comune(comune)

st.subheader(T("a_che_punto"))
H.mostra_avanzamento(comune)

st.subheader(T("i_tuoi_percorsi"))
st.info(H.descrizione_livello(liv))

stato = H.percorsi_disponibili(comune)
for lettera, s in stato.items():
    nome = H.nome_percorso(lettera)
    if s["aperto"]:
        st.success(f"**{lettera} — {nome}**  ·  {T('punteggio')} {s['punteggio']:g}")
    else:
        st.markdown(
            f"<div style='padding:10px 14px;margin-bottom:8px;border-radius:8px;"
            f"background:#F2F3F5;color:#8A94A0;border:1px solid #E3E6EA'>"
            f"<b>{lettera} — {nome}</b><br>"
            f"<span style='font-size:.85rem'>{s['motivo']}</span></div>",
            unsafe_allow_html=True)

if not any(s["aperto"] for s in stato.values()):
    st.warning(T("nessun_percorso"))

st.subheader(T("strumenti"))
H.mostra_prossimi_tool(comune, lingua=LANG)

note = []
if H.accesso_strumento(comune, "avanzato") == "richiesta":
    note.append(T("nota_avanzati"))
if H.accesso_strumento(comune, "fast") == "richiesta":
    note.append(T("nota_fast"))
if note:
    st.caption(T("nota_richiesta", cosa=T("e_cong").join(note),
                 contatto=H.CONTATTO_PROGETTO))

st.divider()
st.subheader(T("ap_sezione"))
st.caption(T("ap_spiega"))
H.action_plan(comune, lingua=LANG, titolo=False)
