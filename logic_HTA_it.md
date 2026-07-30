## ⚙️ Come ragiona il motore di valutazione

Il tool non cerca genericamente chi "usa alte temperature". Incrocia il **codice ATECO** con la **Direttiva Europea RED III** e con le **leggi della termodinamica** per individuare dove l'idrogeno è *chimicamente insostituibile* e dove invece sarebbe uno spreco rispetto alla diretta elettrificazione.

> **Principio guida:** idrogeno *solo* dove non è altrimenti elettrificabile.

---

### 🔢 Lettura del codice (4 cifre)

Il motore legge **solo le prime 4 cifre** del codice (la *Classe*), togliendo i punti e ignorando le cifre finali, che hanno finalità puramente contabili o statistiche.

- Esempio: `24.10.00` → `2410` (Acciaio)
- Se il codice non è nel database prioritario H2, il tool risale al **macro-settore** (prime 2 cifre) ed emette un **alert** chiedendoti di verificare il dato.

---

### 🚦 Gli esiti termodinamici

| Esito | Significato | Esempi tipici |
| :--- | :--- | :--- |
| 🟢 **Assolutamente Necessario** | H2 come materia prima o agente riducente. Nessuna alternativa. | Fertilizzanti/ammoniaca, chimica organica, acciaio DRI |
| 🟢 **Necessario (limiti fisici)** | Grandi forni fusori dove la densità di energia impedisce l'elettrificazione massiva. | Vetro piano e cavo |
| 🟡 **Opzionale / Competizione** | Settori in cui l'idrogeno compete a svantaggio con Biometano e CSS. | Cemento, calce, refrattari, laterizi |
| 🟠 **Alert Elettrificazione** | Trattamenti termici dove induzione o forni elettrici sono più efficienti dell'H2. | Trafilatura, fucinatura, rivestimenti, metallurgia generica |
| 🔴 **Spreco Termodinamico** | Produzione di vapore/energia, edilizia, data center, H2 di scarto. | Vapore, energia di rete, SMR, cokeria |

---

### 🧮 Calcolo del punteggio

Al punteggio base del settore si applicano moltiplicatori e bonus:

1. **Dimensione azienda**
   - Grande → ×1,5
   - Media → ×1,2
   - Piccola → ×1,0
2. **Bonus abilitanti** (si sommano)
   - AIA presente → **+2**
   - Ubicazione in Zona Industriale / consorzio → **+3**
   - Vicinanza al South H2 Corridor → **+3**

Un punteggio elevato indica un candidato prioritario per un piano d'azione sull'idrogeno.

---

### 📝 Compilazione del file (regola d'oro)

- **Obbligatorie:** `nome azienda`, `codice ateco`, `dimensione`.
- **Consigliate:** `processo`, `note`, `ubicazione`, `AIA`. Il tool legge il testo in *processo* e *note* per recuperare aziende borderline (es. parole come "DRI", "forno", "fusione") o escludere falsi positivi (es. H2 di scarto da steam cracking).
