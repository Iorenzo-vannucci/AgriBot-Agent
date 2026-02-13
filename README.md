# 🌱 AgriBot-Agent

**Progetto di Introduzione all'Intelligenza Artificiale** — Variante "Smart Vacuum"

Un agente intelligente che, data un'immagine di una griglia con lettere (scritte a mano o artificiali), riconosce la configurazione dell'ambiente e pianifica autonomamente il percorso ottimale per completare la missione: **innaffiare tutte le piante secche e raggiungere la posizione finale**.

---

## 📖 Descrizione del Dominio

### Ambiente
L'ambiente è una **matrice quadrata N×N** dove ogni cella rappresenta un campo agricolo. Il robot AgriBot deve muoversi nella griglia, **innaffiare tutte le piante secche (D)** e raggiungere la **posizione finale (F)**.

### Legenda Simboli

| Simbolo | Significato | Stato nel progetto |
|---------|-------------|-------------------|
| `S` | Posizione iniziale del robot | ✅ Implementato |
| `F` | Posizione finale del robot | ✅ Implementato |
| `R` | Roccia / cella non accessibile (equiv. a `X` nel PDF) | ✅ Implementato |
| `D` | Pianta secca (da innaffiare) | ✅ Implementato |
| `T` | Stazione di rifornimento acqua | ✅ Implementato |
| `.` | Cella vuota / percorribile | ✅ Implementato |
| `V` | Pianta molto secca (richiede più acqua) | ❌ Da implementare |
| `C` | Cella pulita / pianta già innaffiata | ❌ Da implementare (equiv. a `.`) |

### Vincoli dell'Agente
- **v1**: Il robot può compiere un solo passo alla volta
- **v2**: Il robot si muove solo tra celle adiacenti (su, giù, sinistra, destra — no diagonali)
- **v3**: Il robot non può attraversare celle con rocce (`R`)
- **v4**: Il robot ha un serbatoio d'acqua limitato (`max_water`)
- **v5**: Per innaffiare una pianta `D` serve 1 unità d'acqua
- **v6**: Il robot può ricaricare l'acqua solo nelle stazioni `T`
- **v7**: Il goal è raggiunto quando **tutte le piante sono innaffiate** E il robot è nella posizione `F`

### Azioni Disponibili

| Azione | Precondizione | Effetto | Costo |
|--------|--------------|---------|-------|
| `UP` | cella sopra non è roccia e non è fuori griglia | robot si sposta su | 1 |
| `DOWN` | cella sotto non è roccia e non è fuori griglia | robot si sposta giù | 1 |
| `LEFT` | cella a sinistra non è roccia e non è fuori griglia | robot si sposta a sinistra | 1 |
| `RIGHT` | cella a destra non è roccia e non è fuori griglia | robot si sposta a destra | 1 |
| `WATER` | robot è su una cella `D` e ha acqua > 0 | pianta innaffiata, acqua -1 | 1 |
| `REFILL` | robot è su una stazione `T` e acqua < max | serbatoio pieno | 1 |

---

## 🏗️ Architettura del Progetto

```
AgriBot-Agent/
├── main.py                 # Pipeline: cropping → classificazione → AgriBotProblem → A*/UCS
├── cropping.py             # Modulo: estrazione celle 28×28 da immagine della griglia
├── train.py                # Training del modello CNN su EMNIST (D, F, R, S, T, .)
├── vision_agribot.py       # (vecchio) Visualizzatore celle per mappa L1 — NON collegato
├── agribot_model.keras     # Modello CNN pre-addestrato
├── agribot_map_L1.png      # Immagine di esempio: griglia L1 20×20 (lettere artificiali)
├── test3.png               # Immagine di test: griglia L2 6×6 (lettere a mano)
├── statistiche_training.png # Grafici accuracy/loss del training
├── aima/                   # Libreria AIMA-Python (search.py, utils.py)
│   ├── search.py
│   └── utils.py
└── README.md               # Questo file
```

---

## 🔗 Pipeline Desiderata

```
  ┌────────────┐      ┌─────────────────┐      ┌──────────────────┐      ┌────────────────┐
  │  Immagine  │─────▶│  cropping.py    │─────▶│  Classificazione │─────▶│    main.py     │
  │  in input  │      │  crop()         │      │  model.predict() │      │  A* / UCS      │
  │  (griglia) │      │  → celle 28×28  │      │  celle → lettere │      │  trova piano   │
  └────────────┘      └─────────────────┘      └──────────────────┘      └────────────────┘
                                                        │                        │
                                                        ▼                        ▼
                                                   grid_map =              Sequenza azioni
                                                   [['S','.',..],          + Simulazione
                                                    ['R','D',..]]          visiva
```

---

## 📊 Stato Attuale dei File

### `train.py` — ✅ Completo e funzionante
- Scarica EMNIST Balanced, filtra classi D(13), F(15), R(27), S(28), T(29)
- Aggiunge classe `.` (background) con rumore sintetico
- Addestra CNN con data augmentation e early stopping
- Salva `agribot_model.keras` e `statistiche_training.png`
- **Nessun bug noto**

### `cropping.py` — ⚠️ Quasi pronto, ha dei bug

**Cosa è stato fatto**: il codice è stato wrappato nella funzione `crop(filename, n_rows, n_cols)` ed è importabile da `main.py`. La visualizzazione è dentro `if __name__ == "__main__":`.

**Bug presenti**:

| # | Bug | Dove | Come fixare |
|---|-----|------|-------------|
| 1 | **`crop()` non ha `return cells`** | Fine della funzione `crop()` (dopo riga 137) | Aggiungere `return cells` come ultima riga della funzione. Senza questo, `main.py` riceve `None` |
| 2 | **Usa `N_ROWS`/`N_COLS` invece di `n_rows`/`n_cols`** | Righe 92, 93, 134, 135 | Dentro `crop()` le variabili globali `N_ROWS`/`N_COLS` non esistono più. Devono essere sostituite con i parametri della funzione `n_rows`/`n_cols` |
| 3 | **`if __name__` usa variabili locali di `crop()`** | Righe 139-175 | `cells`, `N_ROWS`, `N_COLS` non sono visibili nel blocco `__main__`. Per testare standalone, bisogna chiamare `crop()` dentro il blocco `__main__` e salvare il risultato |

### `main.py` — ⚠️ Pipeline iniziata, ha dei bug

**Cosa è stato fatto**: rimossa la `grid_map` hardcoded, aggiunto `from cropping import crop`, aggiunto il loop di classificazione (righe 196-205), aggiunto `print_grid` nel simulatore.

**Bug presenti**:

| # | Bug | Dove | Come fixare |
|---|-----|------|-------------|
| 1 | **Manca `import tensorflow as tf`** | In cima al file (righe 1-8) | Aggiungere `import tensorflow as tf` tra gli import |
| 2 | **Normalizzazione sbagliata: `//255` invece di `/255.0`** | Riga 199: `i[2]//255` | `//` è divisione intera → tutto diventa 0 o 1. Deve essere `i[2].astype('float32') / 255.0` per avere valori float tra 0 e 1, come il modello si aspetta |
| 3 | **`result` viene sovrascritto ad ogni iterazione** | Righe 198-204 | Ad ogni ciclo `result` prende la lettera dell'ultima cella. Non viene mai appendata a una struttura. Bisogna costruire `grid_map` dentro il loop |
| 4 | **`grid_map` è inizializzata vuota DOPO il loop** | Riga 205: `grid_map = []` | `grid_map` deve essere costruita DENTRO il loop, accumulando le lettere riga per riga. Esempio: creare una `row = []`, appendere ogni `result`, e quando `j == n_cols - 1` appendere la riga a `grid_map` |
| 5 | **Errore di indentazione nel simulatore** | Righe 296-297 | `print_grid(problem, n.state, n.action)` non è indentato correttamente dentro il `for`. Deve avere 12 spazi (stessa indentazione del `for n in path:` + 4) |
| 6 | **Variabile `shape` inutilizzata** | Riga 200: `shape = normalized_cell.shape` | Non usata da nessuna parte, si può rimuovere |

---

## ✅ TODO — Cose da Fare

### 🔴 Bug da Fixare (il codice non funziona senza questi)

- [ ] **`cropping.py` riga ~137**: Aggiungere `return cells` alla fine della funzione `crop()`
- [ ] **`cropping.py` righe 92-93, 134-135**: Sostituire `N_ROWS` con `n_rows` e `N_COLS` con `n_cols` (parametri della funzione)
- [ ] **`cropping.py` blocco `__main__`**: Chiamare `crop()` dentro `if __name__ == "__main__":` per avere `cells` disponibile alla visualizzazione
- [ ] **`main.py`**: Aggiungere `import tensorflow as tf` in cima al file
- [ ] **`main.py` riga 199**: Cambiare `i[2]//255` → `i[2].astype('float32') / 255.0`
- [ ] **`main.py` righe 196-205**: Riscrivere il loop per costruire `grid_map` come lista di liste:
  ```
  Logica:
  grid_map = []
  row = []
  per ogni (i, j, cella) in cells:
      normalizza cella (float32, /255.0, reshape)
      predict → lettera
      row.append(lettera)
      se j == 19:  # ultima colonna
          grid_map.append(row)
          row = []
  ```
- [ ] **`main.py` riga 297**: Fixare indentazione di `print_grid(problem, n.state, n.action)` — deve essere indentato dentro il `for`

### 🟡 Funzionalità Mancanti (non bloccanti ma richieste dal PDF)

- [ ] **Aggiungere il simbolo `V` (Very Dirty)** — richiede:
  - Aggiungere `V` al `TARGET_MAP` in `train.py` (EMNIST label 31)
  - Ri-addestrare il modello (7 classi totali)
  - In `main.py`: gestire `V` come cella che richiede 2 azioni WATER
- [ ] **Aggiungere `C` (Clean) e `X` (non accessibile)** al modello
- [ ] **Decidere cosa fare con `vision_agribot.py`** — è un duplicato di `cropping.py`, o eliminarlo o integrarlo

### 🟢 Pulizia e Documentazione

- [ ] Rimuovere codice commentato in `main.py` (weeds, pests, energy — righe 48-54, 93-98, ecc.)
- [ ] Rimuovere `shape = normalized_cell.shape` (riga 200, non usata)
- [ ] Scrivere la **relazione** con:
  - Statistiche classificazione (accuracy, confusion matrix)
  - Statistiche ricerca (nodi esplorati UCS vs A*, confronto euristiche)
  - Problemi risolti/irrisolti e dimensioni
- [ ] Testare con **immagini nuove** (richiesto dal PDF alla presentazione)
- [ ] Rendere il path dell'immagine un **argomento da riga di comando** (`sys.argv`)

---

## 📊 Euristiche Implementate

### `h_manhattan` (Euristica 1)
- **Caso A** — tutte le piante innaffiate: distanza Manhattan verso `F` (finish)
- **Caso B** — piante secche rimaste e acqua > 0: distanza Manhattan verso la pianta secca più vicina
- **Caso C** — piante secche rimaste e acqua = 0: distanza Manhattan verso la stazione più vicina

### `h_max_pairwise_distance` (Euristica 2)
Più sofisticata: considera la massima distanza tra tutte le coppie di piante secche rimaste, sommata alla distanza verso la pianta più vicina (o stazione, se senza acqua). Stima meglio il costo totale quando le piante sono sparse.

---

## 🚀 Come Eseguire

### Prerequisites
```bash
source venv/bin/activate
pip install numpy opencv-python matplotlib scipy tensorflow tensorflow-datasets scikit-learn
```

### 1. Training del modello (una sola volta)
```bash
python train.py
# Output: agribot_model.keras, statistiche_training.png
```

### 2. Test cropping standalone
```bash
python cropping.py
# (dopo i fix) Apre finestra con la griglia estratta e slider per navigare le celle
```

### 3. Pipeline completa (dopo i fix)
```bash
python main.py
# Legge immagine → estrae celle → classifica → risolve con UCS e A* → simula
```

---

## 📚 Librerie Utilizzate
- **AIMA-Python** (`aima/search.py`) — `Problem`, `astar_search`, `uniform_cost_search`
- **OpenCV** (`cv2`) — elaborazione immagini, contorni, warp prospettico
- **TensorFlow/Keras** — CNN per classificazione lettere
- **EMNIST** (via `tensorflow_datasets`) — dataset lettere scritte a mano
- **SciPy** — `find_peaks`, `peak_widths` per trovare linee griglia
- **Matplotlib** — visualizzazione celle e grafici training