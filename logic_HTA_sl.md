## ⚙️ Kako razmišlja ocenjevalni motor

Orodje ne išče zgolj podjetij, ki "uporabljajo visoke temperature". Kodo **SKD** primerja z **Evropsko direktivo RED III** in z **zakoni termodinamike**, da ugotovi, kje je vodik *kemično nenadomestljiv* in kje bi pomenil odpadek v primerjavi z neposredno elektrifikacijo.

> **Vodilo:** vodik *samo* tam, kjer elektrifikacija ni mogoča.

---

### 🔢 Branje kode (4 števke)

Motor prebere **samo prve 4 števke** kode (*razred*), odstrani pike in zanemari zadnje števke, ki imajo zgolj statistični namen.

- Primer: `24.100` → `2410` (Jeklo)
- Če kode ni v prednostni vodikovi bazi, orodje uporabi **makro-sektor** (prvi 2 števki) in sproži **opozorilo**, da preverite podatek.

---

### 🚦 Termodinamične ocene

| Ocena | Pomen | Tipični primeri |
| :--- | :--- | :--- |
| 🟢 **Nujno potrebno** | H2 kot surovina ali reducent. Brez alternative. | Gnojila/amonijak, organska kemija, jeklo DRI |
| 🟢 **Potrebno (fizične omejitve)** | Velike talilne peči, kjer gostota energije onemogoča množično elektrifikacijo. | Ravno in votlo steklo |
| 🟡 **Neobvezno / Konkurenca** | Sektorji, kjer je vodik v slabšem položaju glede na biometan in SRF. | Cement, apno, ognjevzdržni izdelki, opeka |
| 🟠 **Opozorilo o elektrifikaciji** | Toplotne obdelave, kjer so indukcijske ali električne peči učinkovitejše od H2. | Vlečenje, kovanje, prevleke, splošna metalurgija |
| 🔴 **Termodinamični odpadek** | Proizvodnja pare/energije, gradbeništvo, podatkovni centri, odpadni H2. | Para, omrežna energija, SMR, koksarne |

---

### 🧮 Izračun ocene

Na osnovno oceno sektorja se uporabijo množitelji in bonusi:

1. **Velikost podjetja**
   - Veliko → ×1,5
   - Srednje → ×1,2
   - Malo → ×1,0
2. **Spodbujevalni bonusi** (seštevajo se)
   - Dovoljenje IED → **+2**
   - Lokacija v industrijski coni / konzorciju → **+3**
   - Bližina koridorja South H2 Corridor → **+3**

Visoka ocena pomeni prednostnega kandidata za vodikov akcijski načrt.

---

### 📝 Izpolnjevanje datoteke (zlato pravilo)

- **Obvezno:** `ime podjetja`, `koda skd`, `velikost`.
- **Priporočeno:** `proces`, `opombe`, `lokacija`, `IED`. Orodje prebere besedilo v poljih *proces* in *opombe*, da prepozna mejna podjetja (npr. besede "DRI", "peč", "litje") ali izloči lažne pozitivne primere (npr. odpadni H2 iz parnega krekinga).
