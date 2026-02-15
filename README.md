# AgriBot-Agent: Autonomous Agricultural Robot
**Progetto di Introduzione all'Intelligenza Artificiale**

AgriBot è un agente intelligente progettato per operare in un ambiente agricolo simulato. Il suo obiettivo è analizzare visivamente una mappa del campo (anche disegnata a mano), identificare piante che necessitano di acqua e pianificare il percorso ottimale per innaffiarle tutte, gestendo risorse limitate (acqua), per poi raggiungere la posizione finale.

---

## Indice
1. [Descrizione del Problema](#descrizione-del-problema)
2. [Architettura del Sistema](#architettura-del-sistema)
3. [Tecnologie Utilizzate](#tecnologie-utilizzate)
4. [Dettagli Implementativi](#dettagli-implementativi)
   - [Estrazione Celle (Grid Cell Extractor)](#1-estrazione-celle-grid-cell-extractor)
   - [Classificazione (CNN)](#2-classificazione-cnn)
   - [Modellazione (Stati e Azioni)](#3-modellazione-stati-e-azioni)
   - [Pianificazione (A* ed Euristiche)](#4-pianificazione-a-ed-euristiche)
   - [Visualizzazione Interattiva](#5-visualizzazione-interattiva)
5. [Installazione ed Esecuzione](#installazione-ed-esecuzione)
6. [Struttura del Progetto](#struttura-del-progetto)
7. [Risultati e Statistiche](#risultati-e-statistiche)

---

## Descrizione del Problema

L'ambiente è rappresentato da una griglia $N \times N$ dove ogni cella può contenere:
- **S (Start)**: Posizione iniziale del robot.
- **F (Finish)**: Posizione finale da raggiungere.
- **R (Rock)**: Ostacolo invalicabile.
- **D (Dry Plant)**: Pianta secca (richiede 1 unità d'acqua).
- **V (Very Dry Plant)**: Pianta molto secca (richiede 2 unità d'acqua).
- **T (Tank)**: Stazione di rifornimento acqua.
- **. (Empty)**: Terreno percorribile (cella vuota).

**Vincoli:**
- Il robot ha un serbatoio con capacità limitata (`max_water`, default = 2).
- Il movimento ha costo 1.
- Innaffiare ha costo 1 e consuma 1 o 2 unità d'acqua (rispettivamente per D e V).
- Ricaricare (Refill) ha costo 1 e riempie il serbatoio al massimo.
- L'obiettivo è innaffiare **tutte** le piante (D e V) e raggiungere F.

---

## Architettura del Sistema

Il progetto è strutturato in una pipeline sequenziale:

```mermaid
graph LR
    A[Immagine Input] --> B[Grid Cell Extractor - CV2]
    B --> C[Classificazione - CNN]
    C --> D[Mappa Logica]
    D --> E[Pathfinding - A* / UCS]
    E --> F[Simulazione Interattiva - Matplotlib]
```

---

## Tecnologie Utilizzate

- **Python 3.12**: Linguaggio principale.
- **OpenCV (`cv2`)**: Per elaborazione immagini (thresholding adattivo Otsu, contour detection, perspective warp, apertura morfologica, componenti connesse).
- **TensorFlow / Keras**: Per la costruzione e il training della CNN, comprensiva di data augmentation integrata nel modello (`RandomRotation`, `RandomZoom`).
- **TensorFlow Datasets (`tfds`)**: Per il download e l'utilizzo del dataset EMNIST Balanced.
- **scikit-learn**: Per lo split stratificato train/validation (`train_test_split`).
- **AIMA-Python** (cartella `aima/`): Libreria base per gli algoritmi di ricerca nello spazio degli stati (A\*, UCS, `InstrumentedProblem`).
- **Matplotlib**: Per la visualizzazione dei grafici di training e della simulazione interattiva con widget (pulsanti Play, Pausa, Avanti, Indietro).
- **NumPy / SciPy**: Per manipolazione matrici e dati.

---

## Dettagli Implementativi

### 1. Estrazione Celle (Grid Cell Extractor)

Il modulo `grid_cell_extractor.py` si occupa di estrarre le singole celle dalla foto della griglia. Il processo è:

1. **Rilevamento della griglia**: L'immagine viene convertita in scala di grigi e binarizzata con soglia Otsu. Si cerca il contorno esterno più grande (`cv2.findContours` + `cv2.contourArea`) che rappresenta il bordo della griglia.

2. **Correzione prospettiva**: I 4 angoli del contorno vengono ordinati (TL, TR, BR, BL) e usati per un **warp prospettico** (`cv2.warpPerspective`) che raddrizza la griglia in un'immagine quadrata di 1000×1000 pixel. Dopo il warp, si applica un'apertura morfologica per pulire il rumore.

3. **Individuazione intervalli celle (estrazione morfologica delle linee)**: Invece di usare proiezioni di pixel e `find_peaks`, si isolano le linee della griglia con **apertura morfologica direzionale**:
   - Un kernel orizzontale lungo estrae solo le linee orizzontali.
   - Un kernel verticale lungo estrae solo le linee verticali.
   - Le celle sono definite come i **gap tra linee consecutive** nella proiezione risultante.
   - Fallback a divisione matematica uniforme se non vengono trovate abbastanza linee.

4. **Pulizia delle celle**: Ogni cella ritagliata viene pulita con `cv2.connectedComponentsWithStats`:
   - Si seleziona la componente connessa più grande (escludendo lo sfondo).
   - Si filtrano componenti troppo piccole (area < 50), sproporzionate (rapporto w/h > 5 o < 0.2), o che assomigliano a linee residue della griglia.
   - La lettera viene centrata in un quadrato con bordo nero e ridimensionata a 28×28 pixel.

### 2. Classificazione (CNN)

Il modulo `train.py` addestra una CNN per riconoscere 7 classi: `['D', 'F', 'R', 'S', 'T', '.', 'V']`.

**Dataset:**
- Si utilizza **EMNIST Balanced** caricato tramite `tensorflow_datasets` (`tfds`).
- Le lettere EMNIST rilevanti vengono mappate alle classi AgriBot: `{13: D, 15: F, 27: R, 28: S, 29: T, 31: V}`.
- La classe **"." (cella vuota)** viene generata sinteticamente: metà celle completamente nere, metà con rumore casuale (valori 0–50), per evitare falsi positivi su celle vuote.
- Lo split train/validation è 80/20, **stratificato** per mantenere proporzioni uguali per ogni classe.

**Architettura del modello:**
```
Input(28×28×1) → RandomRotation(0.1) → RandomZoom(0.1)
→ Conv2D(32, 3×3, ReLU) → MaxPool(2×2) → Dropout(0.2)
→ Conv2D(64, 3×3, ReLU) → MaxPool(2×2) → Dropout(0.2)
→ Flatten → Dense(128, ReLU) → Dropout(0.4) → Dense(7, Softmax)
```

- **Data augmentation**: `RandomRotation` e `RandomZoom` sono integrati direttamente nel modello per simulare variazioni nella scrittura a mano.
- **EarlyStopping**: Monitora `val_loss` con pazienza di 5 epoche, ripristinando i pesi migliori.
- **Output**: Modello salvato come `agribot_model.keras`, grafici di training salvati come `statistiche_training.png`.

### 3. Modellazione (Stati e Azioni)

La classe `AgriBotProblem` (in `main.py`) estende `Problem` di AIMA.

**Stato del robot** (tupla hashable):
```
(posizione, acqua_corrente, frozenset(piante_D), frozenset(piante_V))
```

Le posizioni sono codificate come indice lineare: `index = riga * N + colonna`.

**Azioni possibili** (generate dinamicamente):
| Azione | Condizione | Effetto |
|--------|-----------|---------|
| `UP` / `DOWN` / `LEFT` / `RIGHT` | Cella adiacente non è roccia e non fuori griglia | Sposta il robot |
| `WATER` (su D) | Robot su pianta D e `acqua >= 1` | Rimuove D, consuma 1 acqua |
| `WATER` (su V) | Robot su pianta V e `acqua >= 2` | Rimuove V, consuma 2 acqua |
| `REFILL` | Robot su stazione T e `acqua < max_water` | Riempie il serbatoio al massimo |

**Goal test**: Tutte le piante D e V innaffiate **e** robot in posizione F.

### 4. Pianificazione (A* ed Euristiche)

Il sistema confronta tre strategie di ricerca, tutte basate su `best_first_graph_search` di AIMA:

**Uniform Cost Search (UCS)** — Ricerca cieca che espande il nodo con costo di cammino minore.

**A\* con `h_manhattan`:**
- Se ci sono piante rimaste e ho acqua: distanza Manhattan verso la pianta più vicina.
- Se ci sono piante rimaste e sono a secco: distanza Manhattan verso la stazione più vicina.
- Se tutte le piante sono innaffiate: distanza Manhattan verso F.

**A\* con `h_max_pairwise_Distance` (Euristica Avanzata):**
- Calcola la **massima distanza interna** (diametro) tra tutte le coppie di piante rimaste.
- Se ho acqua: distanza verso la pianta più vicina + diametro.
- Se sono a secco: distanza verso la stazione più vicina + diametro.
- Se tutte le piante sono innaffiate: distanza verso F.
- Questa euristica è molto più informativa: riduce i nodi espansi evitando che il robot "vaghi" inutilmente.

### 5. Visualizzazione Interattiva

La funzione `visualizza_semplice` in `main.py` mostra una simulazione grafica step-by-step della soluzione trovata, implementata con Matplotlib:

- **Griglia colorata**: Rocce (grigio), Stazioni (azzurro), Fine (oro), Piante D (arancione), Piante V (rosso), Bot (verde).
- **Trail del percorso**: Una linea verde semi-trasparente collega tutte le posizioni precedenti del bot.
- **Controlli interattivi**: 4 pulsanti in basso alla finestra:
  - **Play**: Avvia l'animazione automatica.
  - **Pausa**: Ferma l'animazione.
  - **Indietro**: Torna allo step precedente.
  - **Avanti**: Passa allo step successivo.
- **Info in tempo reale**: Titolo con step corrente, azione eseguita, acqua rimanente e piante residue.

---

## Installazione ed Esecuzione

### 1. Prerequisiti: Python e TensorFlow

TensorFlow **non è compatibile** con qualsiasi versione di Python. Prima di iniziare, è fondamentale verificare di avere una versione supportata:

- **TensorFlow supporta solo Python 3.9 – 3.12**. Versioni più vecchie (3.8 e precedenti) o più recenti (3.13+) **non funzionano** e l'installazione fallirà.
- Su **macOS con Apple Silicon** (M1/M2/M3/M4), le versioni recenti di TensorFlow (>= 2.13) includono già il supporto nativo per ARM. Per versioni precedenti era necessario il pacchetto separato `tensorflow-macos`.
- Il Python di sistema di macOS (`/usr/bin/python3`) spesso non è la versione giusta o ha permessi limitati. **Non usarlo direttamente.**

Per verificare la propria versione:
```bash
python3 --version
# Deve restituire Python 3.9.x, 3.10.x, 3.11.x o 3.12.x
```

### 2. Creare un Virtual Environment

Un **virtual environment** è una copia isolata di Python in cui si installano i pacchetti del progetto senza toccare quelli di sistema. Questo è necessario per:
- Evitare conflitti con altri progetti che usano versioni diverse delle stesse librerie.
- Garantire che chiunque cloni il repo possa riprodurre esattamente lo stesso ambiente.
- Non inquinare l'installazione globale di Python.

**Con `venv` (incluso in Python, nessuna installazione aggiuntiva):**

```bash
# Creare l'environment nella cartella del progetto
python3 -m venv env

# Attivare l'environment
# Su macOS / Linux:
source env/bin/activate
# Su Windows:
# env\Scripts\activate
```

Una volta attivato, il terminale mostrerà `(env)` prima del prompt. Da questo momento tutti i comandi `python` e `pip` useranno la versione isolata dentro `env/`. Per disattivarlo basta digitare `deactivate`.

**In alternativa, con [Conda](https://docs.conda.io/)** (utile su macOS Apple Silicon dove gestisce meglio le dipendenze native):

```bash
conda create -n agribot python=3.12
conda activate agribot
```

### 3. Installare le dipendenze con `requirements.txt`

Il file `requirements.txt` contiene l'elenco di tutte le librerie necessarie al progetto:

```
numpy
opencv-python
matplotlib
scipy
tensorflow
tensorflow-datasets
scikit-learn
```

Con l'environment attivo, installarle tutte in un solo comando:

```bash
pip install -r requirements.txt
```

Questo scaricherà e installerà automaticamente ogni pacchetto (e le sue sotto-dipendenze) nella versione compatibile più recente, all'interno dell'environment isolato.

### 4. Esecuzione

> Assicurarsi sempre di aver attivato il virtual environment (`source env/bin/activate` o `conda activate agribot`) prima di eseguire i comandi seguenti.

1. **Training del modello (opzionale se si ha già `agribot_model.keras`):**
   ```bash
   python train.py
   ```
   Scarica EMNIST Balanced via `tfds`, addestra la CNN e salva il modello come `agribot_model.keras`.
   Genera anche `statistiche_training.png` con i grafici di accuracy e loss.

2. **Test estrazione celle (opzionale):**
   ```bash
   python grid_cell_extractor.py
   ```
   Verifica che l'estrazione delle celle dall'immagine funzioni correttamente. Mostra una griglia con le celle estratte e uno slider per navigarle una ad una.

3. **Avvio Agente:**
   ```bash
   python main.py
   ```
   Esegue la pipeline completa:
   - Carica il modello CNN.
   - Estrae le celle dall'immagine (`test3.png`, griglia 6×6).
   - Classifica ogni cella e costruisce la mappa logica.
   - Esegue UCS, A\* con euristica Max Pairwise e A\* con euristica Manhattan.
   - Stampa le statistiche (nodi esplorati, goal test, costo, azioni).
   - Mostra la simulazione grafica interattiva della soluzione A\* Manhattan.

---

## Struttura del Progetto

```
AgriBot-Agent/
├── main.py                    # Core: pipeline completa (visione → modellazione → ricerca → visualizzazione)
├── grid_cell_extractor.py     # Estrazione celle dalla foto della griglia (CV2, morfologia)
├── train.py                   # Addestramento CNN su EMNIST Balanced + classi custom
├── agribot_model.keras        # Modello CNN pre-addestrato (generato da train.py)
├── aima/
│   ├── search.py              # Algoritmi di ricerca (A*, UCS, BFS, DFS, etc.) e InstrumentedProblem
│   └── utils.py               # Utility generiche (PriorityQueue, memoize, distanze, etc.)
├── test3.png                  # Immagine di esempio della griglia 6×6
├── statistiche_training.png   # Grafici accuracy/loss del training (generato da train.py)
├── requirements.txt           # Dipendenze Python del progetto
├── .gitignore
└── README.md
```

---

## Risultati e Statistiche

Esempio di esecuzione su mappa 6×6 complessa (`max_water = 2`):

| Algoritmo | Euristica | Nodi Esplorati | Costo Soluzione | Efficienza |
|-----------|-----------|----------------|-----------------|------------|
| **UCS** | Nessuna | ~6800 | 27 | Baseline |
| **A\*** | Manhattan | ~6200 | 27 | Medio |
| **A\*** | **Max Pairwise** | **~5700** | **27** | **Ottimo** |

L'euristica `Max Pairwise Distance` si è dimostrata la più efficiente, riducendo lo spazio di ricerca di circa il **15–20%** rispetto a UCS, garantendo comunque l'**ottimalità** della soluzione (stessa `path_cost`).

---

**Autori:** Tommaso Lauria, Lorenzo Vannucci
