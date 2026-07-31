## Čemu je orodje namenjeno

Simulator odgovarja na tri vprašanja, v tem vrstnem redu:

1. **Ali je fizično izvedljivo?** Koliko tehta baterija, potrebna za misijo, in ali se napolni v razpoložljivem oknu mirovanja?
2. **Koliko več stane kot dizel?** To je številka, ki jo potrebujete za razpis ali vlogo za financiranje.
3. **Kaj potrebuje območje?** Koliko MWh na leto, koliko ton vodika, koliko obnovljivih zmogljivosti v ozadju.

Razsodba se pojavi **na vrhu**, pred grafi: če tehnologija ne prestane fizičnih omejitev, je ekonomska primerjava nesmiselna.

---

## Od kod prihajajo podatki

Poraba, doseg ter stroški nakupa in vzdrževanja izhajajo iz projektne baze *Comparison H2 elc FF.xlsx* (povprečja popisanih tržnih modelov), zdaj vgrajene v kodo: orodje deluje brez zunanjih prilog.

Parametri o bateriji, koristnem tovoru in življenjski dobi izhajajo iz projektne literature, zlasti iz poročila **Roland Berger, "Vodikovi tovornjaki" (2021)**, in iz eksperimentalnih študij celic pri nizkih temperaturah (*Energies* 2023, 16, 7142; *Energy Engineering* 2025, 122(9)).

---

## Osnovne količine

| Postavka | Enota | Pomen |
|---|---|---|
| `cons_kwh` | kWh/km | energija na vozilu na kilometer |
| `aut` | km | kataloški doseg v standardnih pogojih |
| `maint` | €/km | vzdrževanje |
| `capex` | € | nabavna cena |
| `dpay` | t | izguba koristnega tovora glede na dizel |

Poraba je za vse tehnologije izražena v **energiji**. Naravne enote (litri, kg, kWh) dobimo z deljenjem z energijsko vsebnostjo energenta:

| Energent | kWh na enoto |
|---|---|
| Bencin | 8,76 kWh/l |
| Dizel | 9,91 kWh/l |
| Vodik | 33,33 kWh/kg |
| Elektrika | 1,00 kWh/kWh |

To so dejanske spodnje kurilne vrednosti: dizel 9,91 proti fizični vrednosti 9,94, vodik natančno 33,33.

---

## Dimenzioniranje baterije

Baterija **ni** kataloški podatek: dimenzionirana je glede na misijo.

```
zmogljivost = dnevni km × popravljena poraba × 1,33
```

Koeficient 1,33 je rezerva po Roland Bergerju: izkorišča se 90% stanja napolnjenosti, da se paket ne razgrajuje, plus 20% rezerve dosega.

Iz tega izhajajo vse fizične meritve:

```
teža baterije    = zmogljivost ÷ energijska gostota
čas polnjenja    = zmogljivost ÷ razpoložljiva moč polnjenja
dejanski doseg   = zmogljivost ÷ popravljena poraba
```

**Omejitev teže.** Če potrebna baterija preseže največjo dopustno, se omeji in orodje na to opozori. Največja vrednost je vsota treh postavk: dopustne izgube koristnega tovora vozila, **odstopanja EU v višini 2.000 kg** za vozila brez emisij (Uredba (EU) 2019/1242) in prihranjene teže dizelskega pogonskega sklopa. Ko je baterija omejena, sta možna dva izida: doseg kljub temu pokrije dan, a brez varnostne rezerve, ali pa ga ne pokrije in je treba del energije kupiti na javni polnilnici.

---

## Pogoji uporabe

Orografija in podnebje popravita porabo, **vendar ne enako za vse tehnologije**. To je točka, ki so jo prejšnje različice zgrešile: enak množitelj za vse je učinek v primerjavi izničil.

### Nakloni

| Pot | Množitelj |
|---|---|
| Ravnina | ×1,00 |
| Gričevje | ×1,15 |
| Gore | ×1,35 |

Vozila z električnim pogonom — **tako baterijska kot na gorivne celice** — pri spustu povrnejo energijo z regenerativnim zaviranjem: pri njih se izniči 25% kazni zaradi naklona.

### Ostro zimsko podnebje (< 0 °C)

| Tehnologija | Množitelj |
|---|---|
| Dizel / Bencin | ×1,05 |
| Vodik (FCEV) | ×1,10 |
| Električno (BEV) | ×1,25 |

Razlika ima natančen fizikalni razlog: motor z notranjim zgorevanjem in gorivna celica kabino grejeta z **odvečno toploto**, ki bi jo sicer zavrgla. Baterijsko vozilo jo mora proizvesti z elektriko, odvzeto pogonu. K temu se prišteje upad zmogljivosti celice v mrazu, ki ga eksperimentalne študije ocenjujejo med 6% in 20% pri 0 do −20 °C, z močno odvisnostjo od praznilnega toka.

---

## Življenjska doba baterije

Paket **ne zdrži toliko kot vozilo**. Roland Berger ocenjuje 1.400.000 km za dizelski motor, e-pogon, gorivno celico in vodikove rezervoarje, a le **700.000 km za baterijo** (približno 1.400 ciklov ob polnjenju vsakih 500 km).

```
zamenjave = zaokroži_navzgor(skupni km življenjske dobe ÷ življenjska doba baterije) − 1
```

Strošek zamenjave se prikaže kot **četrti stolpec** v grafu TCO.

**Mraz skrajša življenjsko dobo paketa**, ne le dosega. Pri nizki temperaturi se na anodi odlaga kovinski litij (*lithium plating*): film SEI se odebeli, notranja upornost naraste, v najslabšem primeru pride do notranjega kratkega stika. Ob ostrem podnebju orodje življenjsko dobo zniža za 25%.

---

## Koristni tovor

Pri tovornih vozilih je primerjava v €/km **zavajajoča**: električni tovornjak, ki stane manj na kilometer, a prepelje tri tone manj, zahteva več voženj. Zato se izračuna tudi **€/tonski kilometer**.

Izguba koristnega tovora se za obe tehnologiji izračuna drugače:

- **Električna**: iz baterije, dejansko potrebne za misijo, po odbitku odstopanja EU in prihranjenega pogonskega sklopa. Spreminja se torej s prevoženo razdaljo, orografijo in podnebjem.
- **Vodikova**: vrednost iz literature (Roland Berger), od −1,53 t do −1,90 t za težka vozila pri 700 barih.

---

## Krivulje učenja

Drsnik leta nakupa (2024-2035) linearno interpolira:

| Parameter | 2024 | 2030 |
|---|---|---|
| Energijska gostota baterije | 0,176 kWh/kg | 0,233 kWh/kg |
| Strošek baterije | 167 €/kWh | 161 €/kWh |
| Strošek gorivne celice | 330 €/kW | 210 €/kW |
| Doseg na vodik | izhodišče | +15% |

Cene energentov sledijo trendom, nastavljenim v stranski vrstici: dizel ×1,1, elektrika ×0,9, omrežni vodik ×0,6, lastni vodik ×0,7. Skladni so s projekcijami Roland Bergerja, ki za vodik pri 700 barih napovedujejo prehod s 7,30 €/kg leta 2023 na 4,80 €/kg leta 2030.

---

## Emisije in učinkovitost

Emisije se računajo za **celoten življenjski cikel**, pri čemer se izdelavi vozila prištejejo emisije energenta po pristopu *well-to-wheel*:

| Energent | kg CO₂ na kWh na vozilu |
|---|---|
| Bencin | 0,330 |
| Dizel | 0,307 |
| Omrežna elektrika | 0,215 |
| Lastna elektrika | 0,055 |
| Omrežni vodik | 0,387 |
| Lastni vodik | 0,090 |

Ti faktorji so **medsebojno skladni**: lastni vodik (0,090) izhaja iz fotovoltaike, tako da 0,055 kg/kWh pomnožimo s 55 kWh, potrebnimi za proizvodnjo enega kilograma vodika, in delimo z njegovo energijsko vsebnostjo. 55 kWh/kg pomeni izkoristek elektrolize 60,6%, kar je znotraj dejanskega razpona.

Izkoristek *well-to-wheel* v grafu C je zmnožek dveh izkoristkov: izkoristka dobavne verige (od primarnega vira do energije na vozilu) in izkoristka pogonskega sklopa (od energije na vozilu do kolesa: 40% za motor z notranjim zgorevanjem, 88% za električnega, 52% za gorivno celico).

---

## Kaj spremeniti in kje

| Kaj | Kje v kodi |
|---|---|
| Poraba, doseg, stroški, koristni tovor | slovar `VEICOLI` |
| Energijska vsebnost energentov | `CONV` |
| Faktorji emisij | `F_EMISS` |
| Izkoristki dobavne verige in pogona | `WTT`, `TTW` |
| Kazen zaradi naklona | `ORO` |
| Povračilo z regenerativnim zaviranjem | `REGEN` |
| Podnebne kazni | `FREDDO` |
| Življenjska doba baterije in razgradnja v mrazu | `BATT_VITA_KM`, `VITA_FREDDO` |
| Rezerva pri dimenzioniranju paketa | `BATT_BUFFER` |
| Odstopanje teže in prihranjen pogonski sklop | `DEROGA_UE_KG`, `POWERTRAIN_RISPARMIATO_KG` |

---

## Znane omejitve

Model **ne vključuje stroška ogljika**. Cestni promet je 1. januarja 2025 vstopil v sistem ETS II, tržna faza pa se začne leta 2027: ko se bo ta strošek prenesel na ceno dizla, se bo primerjava premaknila v korist alternativ. Prav tako niso upoštevane razlike v cestninah za vozila brez emisij.

Stroški infrastrukture za polnjenje ali oskrbo niso vključeni in jih je treba prišteti posebej: od 2.000 € za počasno stensko polnilnico do več kot 80.000 € za ultrahitro polnilno mesto za težka vozila ter od 1 do več kot 3 milijone € za visokotlačno vodikovo postajo (glej Orodje 2.8).

Vrednosti izgube koristnega tovora za avtobuse in avtomobile so ocene; vrednosti za težka vozila izhajajo iz literature.
