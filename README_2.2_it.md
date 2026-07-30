## Cosa fa questo strumento

Confronta, **a parità di chilometri percorsi**, quanto costa e quanto inquina una flotta
alimentata a gasolio/benzina, a batteria (BEV) o a idrogeno (FCEV). Non decide al posto tuo:
mostra i numeri e le condizioni in cui una tecnologia diventa preferibile all'altra.

I risultati sono **annui** e riferiti alla flotta intera (non al singolo veicolo).

---

## Da dove vengono i dati

I valori tecnico-economici sono incorporati nel codice e derivano dai fogli
`AUTO`, `CAMION`, `AUTOBUS Urbano`, `AUTOBUS ExtraUrbano` del file *Comparison H2 elc FF.xlsx*,
come **media dei modelli di mercato censiti**. Per ogni combinazione veicolo/alimentazione:

| Voce | Unità | Cosa rappresenta |
|---|---|---|
| `cons` | l/km · kWh/km · kg/km | consumo in condizioni standard |
| `prim` | kWh/km | energia primaria (well-to-wheel) |
| `wtt` | kg CO₂/km | emissioni della filiera del vettore |
| `ttw` | kg CO₂/km | emissioni allo scarico |
| `constr` | kg CO₂ | emissioni di produzione del veicolo (totale, distribuite sugli anni) |
| `maint` | €/km | manutenzione |
| `capex` | € | prezzo d'acquisto del veicolo |
| `range` | km | autonomia dichiarata in condizioni standard |

> **Autonomia:** i valori `range` sono stime di mercato inserite per rendere possibile la
> verifica sulla tratta. Sono l'unico dato **non** derivato dal file Excel originale:
> vanno verificati e allineati ai modelli di riferimento del progetto.

---

## Come si calcola

Con `km_tot = numero veicoli × km/anno per veicolo`:

**Costi (€/anno)**
```
carburante   = consumo_corretto × km_tot × prezzo
manutenzione = maint × km_tot
acquisto     = capex × numero veicoli ÷ durata
TCO          = carburante + manutenzione + acquisto
€/km         = TCO ÷ km_tot
```
L'acquisto è **ripartito sugli anni di vita**: allungando la durata, il costo annuo scende.

**Emissioni (t CO₂/anno)**
```
filiera (WtT) = wtt × consumo_corretto/consumo_base × km_tot ÷ 1000
scarico (TtW) = ttw × consumo_corretto/consumo_base × km_tot ÷ 1000
produzione    = constr × numero veicoli ÷ durata ÷ 1000
```
La produzione del veicolo **non** dipende dalle condizioni di impiego; le altre due sì,
perché seguono il consumo reale.

---

## Le condizioni di impiego

Tre parametri correggono il consumo standard. Il moltiplicatore risultante agisce su
carburante, emissioni da uso, energia primaria e — al contrario — sull'autonomia.

### Orografia

| Percorso | Moltiplicatore |
|---|---|
| Pianura | ×1,00 |
| Collina | ×1,15 |
| Montagna | ×1,35 |

I mezzi con trazione elettrica (**sia BEV sia FCEV**) recuperano energia in discesa con la
frenata rigenerativa: per loro viene annullato il **25%** della penalità. In montagna un
diesel prende ×1,35, un elettrico ×1,26.

### Clima

Il freddo non penalizza tutti allo stesso modo. Riscaldare l'abitacolo di un BEV consuma
energia dalla batteria, e a bassa temperatura la chimica della cella rende meno. Diesel e
celle a combustibile scaldano con il **calore di scarto**, che altrimenti butterebbero via.

| Clima | Termico (diesel/benzina) | Idrogeno (FCEV) | Batteria (BEV) |
|---|---|---|---|
| Mite (> 10 °C) | ×1,00 | ×1,00 | ×1,00 |
| Temperato (0–10 °C) | ×1,02 | ×1,03 | ×1,08 |
| Rigido (< 0 °C) | ×1,05 | ×1,10 | ×1,25 |

### Tratta più lunga senza sosta

È la distanza massima che il mezzo deve coprire prima di potersi fermare. Viene confrontata
con l'**autonomia derata** (`range ÷ moltiplicatore`), perché in salita e al freddo
l'autonomia reale scende:

| Rapporto tratta/autonomia | Esito |
|---|---|
| ≤ 0,8 | 🟢 Tratta coperta |
| 0,8 – 1,0 | 🟡 Margine ridotto |
| > 1,0 | 🔴 Sosta obbligatoria |

Il semaforo è **informativo, non economico**: non modifica il TCO. Serve a vedere quando
una soluzione più economica sulla carta è però **operativamente impraticabile** — il caso
tipico del BEV su lunga percorrenza, dove la sosta di ricarica costa ore di servizio.

---

## Nota importante sui prezzi

Tutti i prezzi dei vettori sono su base **"alla pompa"**: comprendono distribuzione,
compressione a 700 bar per l'idrogeno, e margini della stazione.

Attenzione a non confonderli con i **costi di produzione**, che sono un'altra grandezza:
l'idrogeno grigio da reforming del metano costa circa 2 €/kg *a bocca d'impianto*, ma
erogato in stazione ne costa cinque volte tanto. Nelle versioni precedenti di questo tool il
valore di default dell'idrogeno grigio era proprio il costo di produzione (2 €/kg), e questo
lo faceva risultare **più economico del gasolio** — un artefatto contabile, non un risultato.

Il default attuale è **10 €/kg** erogato. Se vuoi ragionare a costi di produzione, devi
riallineare **tutti** i vettori sulla stessa base, non solo l'idrogeno.

---

## Come leggere i risultati

Le schede sono **numerate** secondo l'ordinamento scelto (costo, emissioni o €/km), quindi
"1" è sempre la migliore rispetto al criterio attivo in quel momento.

Nelle barre delle metriche il **colore** indica se il valore è buono (verde) o problematico
(rosso), e la **lunghezza** la grandezza relativa alle altre alimentazioni. Per costi,
emissioni ed energia vale sempre: più corto è meglio.

I due badge segnalano l'opzione **più economica** e quella **più pulita**: quando non
coincidono, la scelta è un compromesso da motivare, ed è lì che serve il piano d'azione.

---

## Cosa modificare, e dove

| Cosa | Dove nel codice |
|---|---|
| Consumi, costi, emissioni, autonomie | dizionario `VEHICLES` |
| Prezzi di default dei vettori | `FUEL_DEFAULTS` |
| Penalità per pendenza | `ORO_MULT` |
| Recupero da frenata rigenerativa | `REGEN_SHARE` |
| Penalità climatiche per powertrain | `TEMP_MULT` |
| Soglie del semaforo autonomia | funzione `valuta_tratta` |

I moltiplicatori di orografia e clima sono **parametri di progetto**, non misure: sono
ordini di grandezza coerenti con la letteratura sui veicoli elettrici in clima freddo e su
percorsi con pendenze. Vanno rivisti se il progetto adotta valori propri.
