## Kaj orodje počne

Primerja, **ob enaki prevoženi razdalji**, koliko stane in koliko onesnažuje vozni park, ki ga
poganja dizel/bencin, baterija (BEV) ali vodik (FCEV). Ne odloča namesto vas: prikaže številke in
pogoje, v katerih ena tehnologija postane boljša od druge.

Rezultati so **letni** in se nanašajo na celoten vozni park, ne na posamezno vozilo.

---

## Od kod prihajajo podatki

Tehnično-ekonomske vrednosti so vgrajene v kodo in izhajajo iz listov `AUTO`, `CAMION`,
`AUTOBUS Urbano` in `AUTOBUS ExtraUrbano` datoteke *Comparison H2 elc FF.xlsx*, kot
**povprečje popisanih tržnih modelov**. Za vsako kombinacijo vozilo/pogon:

| Postavka | Enota | Kaj predstavlja |
|---|---|---|
| `cons` | l/km · kWh/km · kg/km | poraba v standardnih pogojih |
| `prim` | kWh/km | primarna energija (well-to-wheel) |
| `wtt` | kg CO₂/km | emisije dobavne verige energenta |
| `ttw` | kg CO₂/km | emisije iz izpuha |
| `constr` | kg CO₂ | emisije izdelave vozila (skupaj, porazdeljene na leta) |
| `maint` | €/km | vzdrževanje |
| `capex` | € | nabavna cena vozila |
| `range` | km | deklarirani doseg v standardnih pogojih |

> **Doseg:** vrednosti `range` so tržne ocene, dodane zato, da je preverjanje odseka mogoče.
> To so edini podatki, ki **niso** vzeti iz izvirne datoteke Excel: treba jih je preveriti in
> uskladiti z referenčnimi modeli projekta.

---

## Kako se izračuna

Pri `km_tot = število vozil × km/leto na vozilo`:

**Stroški (€/leto)**
```
gorivo        = popravljena_poraba × km_tot × cena
vzdrževanje   = maint × km_tot
nakup         = capex × število vozil ÷ življenjska doba
TCO           = gorivo + vzdrževanje + nakup
€/km          = TCO ÷ km_tot
```
Nabavna cena je **porazdeljena na leta uporabe**: daljša življenjska doba zniža letni strošek.

**Emisije (t CO₂/leto)**
```
dobavna veriga (WtT) = wtt × popravljena/osnovna poraba × km_tot ÷ 1000
izpuh (TtW)          = ttw × popravljena/osnovna poraba × km_tot ÷ 1000
izdelava             = constr × število vozil ÷ življenjska doba ÷ 1000
```
Izdelava vozila **ni** odvisna od pogojev uporabe; drugi dve postavki sta, ker sledita dejanski
porabi.

---

## Pogoji uporabe

Trije parametri popravijo standardno porabo. Nastali množitelj vpliva na gorivo, emisije pri
uporabi in primarno energijo — ter obratno na doseg.

### Orografija

| Pot | Množitelj |
|---|---|
| Ravnina | ×1,00 |
| Gričevje | ×1,15 |
| Gore | ×1,35 |

Vozila z električnim pogonom (**tako BEV kot FCEV**) del energije pri spustu povrnejo z
regenerativnim zaviranjem: pri njih se izniči **25%** kazni zaradi naklona. V gorah dizel dobi
×1,35, električno vozilo ×1,26.

### Podnebje

Mraz ne prizadene vseh enako. Ogrevanje kabine pri BEV porablja energijo iz baterije, pri nizkih
temperaturah pa je kemija celice manj učinkovita. Dizelski motorji in gorivne celice kabino
grejejo z **odvečno toploto**, ki bi jo sicer zavrgli.

| Podnebje | Toplotni (dizel/bencin) | Vodik (FCEV) | Baterija (BEV) |
|---|---|---|---|
| Milo (> 10 °C) | ×1,00 | ×1,00 | ×1,00 |
| Zmerno (0–10 °C) | ×1,02 | ×1,03 | ×1,08 |
| Ostro (< 0 °C) | ×1,05 | ×1,10 | ×1,25 |

### Najdaljši odsek brez postanka

To je največja razdalja, ki jo mora vozilo prevoziti, preden se lahko ustavi. Primerja se z
**zmanjšanim dosegom** (`range ÷ množitelj`), saj se v klancu in na mrazu dejanski doseg zniža:

| Razmerje odsek/doseg | Izid |
|---|---|
| ≤ 0,8 | 🟢 Odsek pokrit |
| 0,8 – 1,0 | 🟡 Majhna rezerva |
| > 1,0 | 🔴 Postanek obvezen |

Semafor je **informativen, ne ekonomski**: ne spremeni TCO. Pokaže, kdaj je na papirju cenejša
rešitev **operativno neizvedljiva** — značilen primer je BEV na dolgih razdaljah, kjer postanek za
polnjenje pomeni izgubo ur obratovanja.

---

## Pomembna opomba o cenah

Vse cene energentov so na podlagi **"na točilni napravi"**: vključujejo distribucijo, stiskanje na
700 bar pri vodiku in maržo postaje.

Ne zamenjujte jih s **proizvodnimi stroški**, ki so druga količina: sivi vodik iz reformiranja
metana stane približno 2 €/kg *na izhodu iz obrata*, a petkrat toliko, ko je izdan na postaji. V
prejšnjih različicah tega orodja je bila privzeta vrednost za sivi vodik prav proizvodni strošek
(2 €/kg), zaradi česar je izšel **ceneje od dizla** — to je računovodski artefakt, ne rezultat.

Trenutna privzeta vrednost je **10 €/kg** izdanega vodika. Če želite računati s proizvodnimi
stroški, morate na isto osnovo preračunati **vse** energente, ne le vodika.

---

## Kako brati rezultate

Kartice so **številčene** glede na izbrano razvrstitev (strošek, emisije ali €/km), zato je "1"
vedno najboljša možnost glede na trenutno aktivno merilo.

V stolpcih metrik **barva** povede, ali je vrednost dobra (zelena) ali problematična (rdeča),
**dolžina** pa njeno velikost glede na druge pogone. Za stroške, emisije in energijo velja vedno:
krajše je bolje.

Oznaki označujeta **najcenejšo** in **najčistejšo** možnost: kadar se ne ujemata, je izbira
kompromis, ki ga je treba utemeljiti — in prav tam nastopi akcijski načrt.

---

## Kaj spremeniti in kje

| Kaj | Kje v kodi |
|---|---|
| Poraba, stroški, emisije, dosegi | slovar `VEHICLES` |
| Privzete cene energentov | `FUEL_DEFAULTS` |
| Kazen zaradi naklona | `ORO_MULT` |
| Povračilo z regenerativnim zaviranjem | `REGEN_SHARE` |
| Podnebne kazni po pogonu | `TEMP_MULT` |
| Mejne vrednosti semaforja dosega | funkcija `valuta_tratta` |

Množitelji za orografijo in podnebje so **projektni parametri, ne meritve**: gre za velikostne
rede, skladne z literaturo o električnih vozilih v mrzlem podnebju in na poteh z nakloni. Če
projekt sprejme lastne vrednosti, jih je treba popraviti.
