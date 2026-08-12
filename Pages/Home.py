import streamlit as st
import h2ready as H

st.set_page_config(page_title="H2READY · Percorso A", page_icon="🅰️", layout="wide")

comune = H.blocco_accesso("Percorso A — Domanda di idrogeno", percorso="A")
if comune is None:
    st.stop()

st.markdown("""
### Percorso A — Domanda di idrogeno

Tre strumenti, da compilare nell'ordine indicato nella barra laterale:

1. **Scouting HTA** — quali industrie del territorio hanno un fabbisogno reale
2. **Flotte e TCO** — quali mezzi conviene convertire, e a che costo
3. **Riscaldamento** — il fabbisogno termico degli edifici pubblici

I risultati confluiscono nel percorso B, che li usa per dimensionare la produzione.
""")

H.mostra_avanzamento(comune)
st.divider()
H.mostra_prossimi_tool(comune, lingua="it")
