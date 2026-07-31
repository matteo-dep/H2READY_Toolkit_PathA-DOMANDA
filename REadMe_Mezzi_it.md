## A cosa serve

Questo simulatore risponde a tre domande, in quest'ordine:

1. **Ce la faccio fisicamente?** La batteria necessaria alla missione quanto pesa, e si ricarica nella finestra di sosta disponibile?
2. **Quanto mi costa in più del diesel?** È il numero che serve per un bando o una domanda di finanziamento.
3. **Cosa serve al territorio?** Quanti MWh all'anno, quante tonnellate di idrogeno, quanta potenza rinnovabile dietro.

Il verdetto compare **in cima**, prima dei grafici: se una tecnologia non regge i vincoli fisici, il confronto economico è inutile.

---

## Da dove vengono i dati

Consumi, autonomie, costi di acquisto e manutenzione derivano dal database di progetto *Comparison H2 elc FF.xlsx* (medie dei modelli di mercato censiti), ora incorporati nel codice: il tool gira senza allegati esterni.

I parametri su batteria, carico utile e vita utile vengono dalla letteratura di progetto, in particolare dal report **Roland Berger, "Camion a idrogeno" (2021)** e dagli studi sperimentali sulle celle a bassa temperatura (*Energies* 2023, 16, 7142; *Energy Engineering* 2025, 122(9)).

---

## Le grandezze fondamentali

| Voce | Unità | Significato |
|---|---|---|
| `cons_kwh` | kWh/km | energia a bordo del veicolo per chilometro |
| `aut` | km | autonomia di catalogo in condizioni standard |
| `maint` | €/km | manutenzione |
| `capex` | € | prezzo d'acquisto |
| `dpay` | t | perdita di carico utile rispetto al diesel |

Il consumo è espresso in **energia** per tutte le tecnologie. Le unità naturali (litri, kg, kWh) si ricavano dividendo per il contenuto energetico del vettore:

| Vettore | kWh per unità |
|---|---|
| Benzina | 8,76 €/l |
| Diesel | 9,91 kWh/l |
| Idrogeno | 33,33 kWh/kg |
| Elettricità | 1,00 kWh/kWh |

Questi sono poteri calorifici inferiori reali: il diesel a 9,91 contro un valore fisico di 9,94, l'idrogeno esatto a 33,33.

---

## Dimensionamento della batteria

La batteria **non** è un dato di catalogo: viene dimensionata sulla missione.

```
capacità = km giornalieri × consumo corretto × 1,33
```

Il coefficiente 1,33 è il margine di Roland Berger: si sfrutta il 90% dello stato di carica per non degradare il pacco, più un 20% di riserva di autonomia.

Da qui discendono tutte le metriche fisiche:

```
peso batteria    = capacità ÷ densità energetica
tempo di ricarica = capacità ÷ potenza di ricarica disponibile
autonomia reale   = capacità ÷ consumo corretto
```

**Limite di peso.** Se la batteria necessaria supera il massimo ammissibile, viene troncata e il tool lo segnala. Il massimo è la somma di tre voci: la tolleranza sulla perdita di carico utile del mezzo, la **deroga UE di 2.000 kg** per i veicoli a zero emissioni (Regolamento UE 2019/1242) e il peso del powertrain diesel risparmiato. Quando la batteria è troncata possono succedere due cose: l'autonomia copre comunque la giornata ma senza margine di sicurezza, oppure non la copre, e allora una quota di energia va comprata a ricarica pubblica.

---

## Condizioni di impiego

Orografia e clima correggono il consumo, **ma non allo stesso modo per tutte le tecnologie**. Questo è il punto che nelle versioni precedenti era sbagliato: applicare lo stesso moltiplicatore a tutti annullava l'effetto nel confronto.

### Pendenze

| Percorso | Moltiplicatore |
|---|---|
| Pianura | ×1,00 |
| Collinare | ×1,15 |
| Montagna | ×1,35 |

I mezzi a trazione elettrica — **sia batteria sia fuel cell** — recuperano energia in discesa con la frenata rigenerativa: per loro viene annullato il 25% della penalità.

### Clima invernale rigido (< 0 °C)

| Tecnologia | Moltiplicatore |
|---|---|
| Diesel / Benzina | ×1,05 |
| Idrogeno (FCEV) | ×1,10 |
| Elettrico (BEV) | ×1,25 |

La differenza ha una ragione fisica precisa: motore termico e cella a combustibile scaldano l'abitacolo con il **calore di scarto**, che altrimenti butterebbero via. Il veicolo a batteria deve produrlo con energia elettrica sottratta alla trazione. A questo si somma il calo di prestazione della cella al freddo, che gli studi sperimentali quantificano tra il 6% e il 20% tra 0 e −20 °C, con dipendenza forte dalla corrente di scarica.

---

## Vita della batteria

Il pacco **non dura quanto il mezzo**. Roland Berger stima 1.400.000 km per motore diesel, e-drive, cella a combustibile e serbatoi di idrogeno, ma solo **700.000 km per la batteria** (circa 1.400 cicli con ricarica ogni 500 km).

```
sostituzioni = arrotonda_per_eccesso(km totali di vita ÷ vita batteria) − 1
```

Il costo della sostituzione compare come **quarta barra** nel grafico del TCO.

**Il freddo accorcia la vita del pacco**, non solo l'autonomia. A bassa temperatura si deposita litio metallico sull'anodo (*lithium plating*): il film SEI si ispessisce, la resistenza interna cresce e nei casi peggiori si arriva al corto circuito interno. Con clima rigido il tool riduce la vita utile del 25%.

---

## Carico utile

Per i mezzi merci il confronto in €/km è **fuorviante**: un camion elettrico che costa meno al chilometro ma porta tre tonnellate in meno di merce richiede più viaggi. Per questo si calcola anche il **€/tonnellata-km**.

La perdita di carico utile è calcolata in modo diverso per le due tecnologie:

- **Elettrico**: dalla batteria realmente necessaria alla missione, al netto della deroga UE e del powertrain risparmiato. Varia quindi con percorrenza, orografia e clima.
- **Idrogeno**: valore di letteratura (Roland Berger), da −1,53 t a −1,90 t per i mezzi pesanti a 700 bar.

---

## Curve di apprendimento

Lo slider dell'anno di acquisto (2024-2035) interpola linearmente:

| Parametro | 2024 | 2030 |
|---|---|---|
| Densità batteria | 0,176 kWh/kg | 0,233 kWh/kg |
| Costo batteria | 167 €/kWh | 161 €/kWh |
| Costo cella a combustibile | 330 €/kW | 210 €/kW |
| Autonomia idrogeno | riferimento | +15% |

I prezzi dei vettori seguono i trend impostati nella barra laterale: diesel ×1,1, elettricità ×0,9, idrogeno da rete ×0,6, idrogeno autoprodotto ×0,7. Sono coerenti con le proiezioni Roland Berger, che per l'idrogeno a 700 bar indicano un passaggio da 7,30 €/kg nel 2023 a 4,80 €/kg nel 2030.

---

## Emissioni ed efficienza

Le emissioni sono calcolate sul **ciclo di vita**, sommando produzione del veicolo ed emissioni del vettore energetico *well-to-wheel*:

| Vettore | kg CO₂ per kWh a bordo |
|---|---|
| Benzina | 0,330 |
| Diesel | 0,307 |
| Elettricità di rete | 0,215 |
| Elettricità autoprodotta | 0,055 |
| Idrogeno da rete | 0,387 |
| Idrogeno autoprodotto | 0,090 |

Questi fattori sono **internamente coerenti**: l'idrogeno autoprodotto (0,090) si ricava dal fotovoltaico moltiplicando 0,055 kg/kWh per i 55 kWh necessari a produrre un chilogrammo di idrogeno e dividendo per il suo contenuto energetico. I 55 kWh/kg implicano un rendimento di elettrolisi del 60,6%, dentro la forchetta reale.

L'efficienza *well-to-wheel* mostrata nel grafico C è il prodotto di due rendimenti: quello della filiera (dalla fonte primaria all'energia a bordo) e quello del powertrain (dall'energia a bordo alla ruota, 40% per un motore termico, 88% per un elettrico, 52% per una cella a combustibile).

---

## Cosa modificare, e dove

| Cosa | Dove nel codice |
|---|---|
| Consumi, autonomie, costi, carico utile | dizionario `VEICOLI` |
| Contenuti energetici dei vettori | `CONV` |
| Fattori di emissione | `F_EMISS` |
| Rendimenti di filiera e powertrain | `WTT`, `TTW` |
| Penalità per pendenza | `ORO` |
| Recupero da frenata rigenerativa | `REGEN` |
| Penalità climatiche | `FREDDO` |
| Vita della batteria e degrado da freddo | `BATT_VITA_KM`, `VITA_FREDDO` |
| Margine di dimensionamento del pacco | `BATT_BUFFER` |
| Deroga di peso e powertrain risparmiato | `DEROGA_UE_KG`, `POWERTRAIN_RISPARMIATO_KG` |

---

## Limiti noti

Il modello **non include il costo del carbonio**. Il trasporto stradale è entrato nel sistema ETS II dal 1° gennaio 2025, con la fase di mercato dal 2027: quando quel costo si scaricherà sul prezzo del gasolio, il confronto si sposterà a favore delle alternative. Allo stesso modo non sono considerate le differenziazioni di pedaggio per i veicoli a zero emissioni.

Non sono inclusi i costi dell'infrastruttura di ricarica o rifornimento, che vanno sommati a parte: da 2.000 € per una wallbox lenta a oltre 80.000 € per una colonnina ultra-fast per mezzi pesanti, e da 1 a oltre 3 milioni di euro per una stazione a idrogeno ad alta pressione (vedi Tool 2.8).

I valori di perdita di carico utile per autobus e automobili sono stime; quelli dei mezzi pesanti vengono dalla letteratura.
