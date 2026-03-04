## AgriBot Agent

AgriBot Agent è un progetto di **pianificazione intelligente per un robot agricolo** su una griglia.  
Il flusso completo è:

- **addestrare** una rete neurale convoluzionale (CNN) che riconosce lettere scritte a mano (D, F, R, S, T, V e celle vuote) a partire dal dataset **EMNIST**;
- **estrarre automaticamente** le singole celle da un’immagine della griglia del campo (foto o scansione) usando OpenCV;
- **classificare ogni cella** (pianta secca, molto secca, roccia, stazione, start, finish, vuota…);
- costruire un **problema di ricerca** (A\* e Uniform Cost Search, UCS) tramite le utility AIMA per trovare un piano ottimale per il robot;
- **visualizzare il percorso** e le azioni del robot su una griglia interattiva con Matplotlib.

Tutto il codice è in **Python 3.10**, requisito fondamentale perché **TensorFlow** usato nel progetto non è compatibile con tutte le versioni di Python.

---

## Struttura del progetto

- **`main.py`**  
  - Carica il modello Keras salvato (`agribot_model.keras`).  
  - Usa `grid_cell_extractor.crop(...)` per dividere l’immagine della griglia (`test3.png`) in celle 28×28 in scala di grigi.  
  - Classifica ogni cella con il modello CNN nelle etichette `['D', 'F', 'R', 'S', 'T', '.', 'V']`.  
  - Costruisce una matrice `grid_map` e il problema di ricerca `AgriBotProblem`.  
  - Esegue tre algoritmi:
    - `ucs()` → Uniform Cost Search (UCS);
    - `a_star()` → A\* con euristica `h_max_pairwaise_Distance`;
    - `a_star1()` → A\* con euristica `h_manhattan`.  
  - Stampa a terminale lo stato della griglia e mostra una **visualizzazione grafica interattiva** (pulsanti Play, Pausa, Indietro, Avanti).

- **`train.py`**  
  - Scarica il dataset `emnist/balanced` tramite `tensorflow_datasets`.  
  - Filtra solo le lettere di interesse e mappa le etichette EMNIST sugli indici del modello (`TARGET_MAP`).  
  - Genera esempi di **celle vuote con rumore** per rendere il modello robusto.  
  - Costruisce e addestra una **CNN** (Keras Sequential) con data augmentation (rotazioni, zoom).  
  - Salva il modello addestrato in `agribot_model.keras`.  
  - Salva `statistiche_training.png` con i grafici di accuracy e loss train/validation.

- **`grid_cell_extractor.py`**  
  - Legge un’immagine di una griglia (es. `test3.png`).  
  - Trova il contorno principale, lo “raddrizza” (warp prospettico) e lo porta a dimensione fissa (`DIM = 1000`).  
  - Usa operazioni morfologiche per **individuare le linee della griglia** e definire automaticamente le celle.  
  - Per ogni cella:
    - pulisce i bordi e rimuove il rumore;  
    - estrae il componente con area maggiore (la lettera scritta);  
    - controlla forme troppo sottili o allungate (linee della griglia) e le scarta;  
    - ricentra e ridimensiona a 28×28 pixel.  
  - Ritorna una lista di tuple `(i, j, immagine_cella)`.

- **Cartella `aima/` (almeno `search.py`, `utils.py`)**  
  - Contiene funzioni e classi per problemi di ricerca (ad es. `Problem`, `Node`, `astar_search`, `uniform_cost_search`, `InstrumentedProblem`) basate sul materiale AIMA.  
  - `main.py` aggiunge questa cartella al `sys.path` e importa da qui gli algoritmi di ricerca.

- **`.python-version`**  
  - Indica la versione di Python richiesta: **3.10.13**.  
  - Se usi `pyenv`, questa versione verrà selezionata automaticamente nella directory del progetto.

---

## Requisiti di sistema

- **Sistema operativo**:  
  - macOS, Linux (e Windows tramite WSL o Conda; consigliato comunque un ambiente Unix-like).
- **Python**:  
  - **Python 3.10.x obbligatorio** (il file `.python-version` indica 3.10.13).  
  - Versioni 3.11 o 3.12 possono dare problemi con TensorFlow.
- **RAM**:  
  - Almeno **8 GB consigliati** per addestrare il modello EMNIST (meglio 16 GB).
- **Connessione Internet**:  
  - Necessaria almeno una volta per scaricare il dataset `emnist/balanced` tramite `tensorflow_datasets`.

---

## Perché è necessario Python 3.10 (TensorFlow)

TensorFlow supporta solo un sottoinsieme di versioni Python.  
La versione di Python è critica perché:

- il **wheel** `tensorflow` per macOS/Linux è rilasciato solo per alcune versioni (es. 3.8, 3.9, 3.10 nei rami TF 2.x);  
- con versioni di Python non supportate (es. 3.12) `pip install tensorflow` potrebbe:
  - non trovare un wheel compatibile,  
  - forzare il build da sorgente (estremamente lento e complesso),  
  - oppure semplicemente fallire.

Per evitare tutti questi problemi, il progetto è pensato per **Python 3.10.13**.  
Se hai un’altra versione di Python come predefinita, nelle sezioni successive trovi come **cambiarla e isolare l’ambiente**.

---

## Installazione di Python 3.10 e cambio versione

Di seguito tre modi tipici per assicurarti di usare **Python 3.10**:

### 1. Usare pyenv (consigliato su macOS/Linux)

1. **Installa pyenv**  
   Su macOS con Homebrew:

   ```bash
   brew update
   brew install pyenv
   ```

   Su Linux, segui la guida ufficiale (`pyenv` su GitHub) oppure il tuo package manager.

2. **Installa Python 3.10.13 con pyenv**:

   ```bash
   pyenv install 3.10.13
   ```

3. **Imposta la versione locale del progetto** (usa la directory del repo):

   ```bash
   cd /percorso/AgriBot-Agent
   pyenv local 3.10.13
   ```

   Questo comando:
   - crea/usa il file `.python-version` con scritto `3.10.13`;  
   - fa sì che, all’interno della cartella del progetto, il comando `python` (o `python3`) punti a **Python 3.10.13** gestito da pyenv.

4. **Verifica che la versione attiva sia corretta**:

   ```bash
   python --version
   # oppure
   python3 --version
   ```

   L’output deve essere simile a:

   ```text
   Python 3.10.13
   ```

### 2. Usare Conda (Anaconda / Miniconda)

Se preferisci Conda:

1. **Crea un nuovo ambiente**:

   ```bash
   conda create -n agribot python=3.10
   ```

2. **Attiva l’ambiente**:

   ```bash
   conda activate agribot
   ```

3. **Verifica la versione**:

   ```bash
   python --version
   # deve riportare Python 3.10.x
   ```

Conda gestirà per te la versione di Python. In questo caso puoi ignorare `.python-version` o lasciarlo come promemoria.

### 3. Usare direttamente python3.10 (senza pyenv/Conda)

Se il tuo sistema ha già un eseguibile `python3.10` installato:

1. **Crea un virtualenv dedicato** nella cartella del progetto:

   ```bash
   cd /percorso/AgriBot-Agent
   python3.10 -m venv .venv
   ```

2. **Attiva il virtualenv**:

   - su macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

   - su Windows (PowerShell):

     ```powershell
     .venv\Scripts\Activate.ps1
     ```

3. **Controlla la versione**:

   ```bash
   python --version
   # Python 3.10.x
   ```

---

## Installazione delle dipendenze Python

Una volta che **Python 3.10** è attivo (con uno dei metodi sopra) e il tuo ambiente virtuale è attivato, installa i pacchetti necessari.

Comandi tipici:

```bash
cd /percorso/AgriBot-Agent

pip install --upgrade pip

pip install \
  tensorflow \
  tensorflow-datasets \
  numpy \
  matplotlib \
  opencv-python \
  scikit-learn
```

Note importanti:

- **Versione di TensorFlow**: scegli una versione **2.x compatibile con Python 3.10** (es. 2.15.x o versione indicata dalla documentazione ufficiale al momento in cui installi).  
  In caso di dubbi, consulta la tabella di compatibilità sul sito TensorFlow.
- Su macOS con Apple Silicon (M1/M2/M3), potresti voler installare le varianti specifiche (`tensorflow-macos`, ecc.) seguendo le istruzioni ufficiali.

---

## Dataset EMNIST e primo download

Il training (`train.py`) usa il dataset `emnist/balanced` tramite **TensorFlow Datasets (tfds)**:

- al **primo esecuzione**, `tfds.load('emnist/balanced', ...)` scaricherà automaticamente il dataset;  
- la posizione predefinita del dataset è in una cartella simile a `~/.tensorflow-datasets` (dipende dal sistema);
- il download può richiedere **diversi minuti** e qualche GB di spazio su disco.

Se vuoi evitare di scaricare ogni volta:

- mantieni la stessa cartella utente (`HOME`) e non cancellare la directory `tensorflow_datasets`;
- una volta scaricato, i successivi `train.py` riuseranno i dati in cache.

---

## Flusso di lavoro: training del modello (`train.py`)

### 1. Panoramica di `train.py`

`train.py` esegue le seguenti operazioni:

- **caricamento dati**:  
  - chiama `load_data_tfds()` che scarica/legge il dataset `emnist/balanced`;  
  - filtra solo alcune lettere (D, F, R, S, T e V) usando la mappa `TARGET_MAP`;  
  - genera esempi di **celle vuote** con o senza rumore per rappresentare `"."` (celle senza contenuto);  
  - normalizza le immagini in \[0, 1\] e le ridimensiona a 28×28×1;  
  - converte le etichette in **one-hot** (`to_categorical`) con 7 classi (`CLASSES = ['D', 'F', 'R', 'S', 'T', '.', 'V']`).

- **definizione del modello** (`build_model()`):  
  - architettura CNN sequenziale con:
    - layer di input `(28, 28, 1)`;  
    - data augmentation: `RandomRotation(0.1)`, `RandomZoom(0.1)`;  
    - due blocchi `Conv2D + MaxPooling2D + Dropout`;  
    - `Flatten`, `Dense(128, activation='relu')`, `Dropout`;  
    - `Dense(7, activation='softmax')` per le 7 classi finali.

- **training**:
  - suddivide il dataset in **train/validation** (`train_test_split` con `test_size=0.2` e `stratify=Y`);  
  - imposta un `EarlyStopping` su `val_loss` con `patience=5` e `restore_best_weights=True`;  
  - esegue il `model.fit(...)` (nel codice è impostato `epochs=1` ma puoi aumentarlo se vuoi migliori prestazioni).

- **salvataggio risultati**:
  - salva il modello in `agribot_model.keras`;  
  - genera i grafici e li salva in `statistiche_training.png`.

### 2. Come lanciare il training

Assicurati di:

- avere l’ambiente virtuale attivo (Python 3.10);  
- aver installato tutte le dipendenze (`tensorflow`, `tensorflow-datasets`, `numpy`, `matplotlib`, `opencv-python`, `scikit-learn`).

Poi esegui:

```bash
cd /percorso/AgriBot-Agent
python train.py
```

Durante la prima esecuzione vedrai messaggi tipo:

- download del dataset EMNIST;  
- avanzamento delle epoche di training;  
- barre di progresso Keras.

Al termine dovresti ottenere:

- **file modello**: `agribot_model.keras` (nella root del progetto);  
- **grafico**: `statistiche_training.png`.

Se questi file esistono già e sei soddisfatto del modello, puoi saltare il training e passare direttamente a `main.py`.

---

## Flusso di lavoro: uso del modello per pianificare (`main.py`)

### 1. Preparare l’immagine della griglia

`main.py` si aspetta un file immagine, per default:

- nome file: **`test3.png`**  
- posizionato nella **cartella principale del progetto** (stessa dove si trova `main.py`).

Questa immagine dovrebbe essere:

- una griglia con **N_ROWS × N_COLS** celle (nel codice: 6 × 6);  
- ogni cella contiene una lettera che rappresenta un tipo di cella:
  - `S` → posizione di **Start** del robot;  
  - `F` → **Finish** (posizione di arrivo/obiettivo finale);  
  - `R` → **Roccia** / ostacolo non attraversabile;  
  - `T` → **Stazione di rifornimento acqua**;  
  - `D` → Pianta **secca** da irrigare (consuma 1 unità d’acqua);  
  - `V` → Pianta **molto secca** da irrigare (consuma 2 unità d’acqua);  
  - `.` o cella vuota → terreno neutro / senza vincoli specifici.

Se vuoi usare un’immagine diversa:

- copia la tua immagine (ad es. `campo1.png`) nella root del progetto;  
- apri `main.py` e modifica la riga:

```python
cells = crop("test3.png", N_ROWS, N_COLS)
```

in:

```python
cells = crop("campo1.png", N_ROWS, N_COLS)
```

Assicurati che:

- la griglia reale dell’immagine corrisponda ai valori `N_ROWS` e `N_COLS` definiti in `main.py`;  
- le lettere siano leggibili, con sufficiente contrasto, e abbastanza centrali nelle celle.

### 2. Cosa fa `main.py` passo per passo

1. **Import e setup**  
   - aggiunge la cartella `aima` al `sys.path`;  
   - importa TensorFlow, NumPy, Matplotlib ed i moduli AIMA (ricerca).

2. **Caricamento modello**  

   ```python
   model = tf.keras.models.load_model("agribot_model.keras")
   ```

   - è fondamentale che questo file esista nella root del progetto (creato da `train.py` o fornito già pronto).

3. **Estrazione delle celle dalla griglia**  

   ```python
   N_ROWS = 6
   N_COLS = 6
   cells = crop("test3.png", N_ROWS, N_COLS)
   ```

   - `crop` (da `grid_cell_extractor.py`) restituisce una lista di triple `(i, j, cell_img)`;  
   - ogni `cell_img` è già una immagine 28×28 adatta al modello.

4. **Classificazione di ogni cella**  

   Per ogni `(i, j, cell_img)`:

   - normalizza l’immagine \(\in [0,1]\);  
   - cambia forma in `(1, 28, 28, 1)`;  
   - esegue `model.predict(...)` e prende la classe con `np.argmax`;  
   - mappa l’indice numerico in una lettera tra `LABELS = ['D', 'F', 'R', 'S', 'T', '.', 'V']`;  
   - costruisce `grid_map` come matrice di lettere (`N_ROWS × N_COLS`).

5. **Definizione del problema di pianificazione** (`AgriBotProblem`)

   - eredita da `Problem` (AIMA);  
   - lo **stato** ha la forma:

     ```python
     (position, water, dry, very_dry)
     ```

     dove:
     - `position` è l’indice della cella corrente (0…N²-1);  
     - `water` è l’acqua residua nel serbatoio;  
     - `dry` è un `frozenset` con gli indici delle piante secche D da irrigare;  
     - `very_dry` è un `frozenset` con gli indici delle piante V da irrigare.

   - la **griglia** viene convertita in:
     - `rocks` (insieme di posizioni con `R`);  
     - `station` (posizioni con `T`);  
     - `start_position` (`S`);  
     - `finish_position` (`F`).

   - il **goal** è raggiunto quando:

     - non ci sono più piante secche o molto secche: `len(dry) == 0` e `len(very_dry) == 0`;  
     - `position == finish_position`.

   - le **azioni** possibili includono:
     - movimenti: `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"` (solo se non ci sono rocce);  
     - `"WATER"`: se sulla cella attuale c’è una pianta D o V e si ha acqua sufficiente;  
     - `"REFILL"`: se si è su una cella stazione `T` e il serbatoio non è pieno.

6. **Algoritmi di ricerca**

   `main.py` definisce e lancia:

   - `ucs()`:
     - usa `uniform_cost_search` con `InstrumentedProblem` per raccogliere statistiche;  
     - stampa numero di nodi esplorati, goal test e costo totale;  
     - visualizza la soluzione con `visualizza_semplice(...)`.

   - `a_star()`:
     - esegue A\* con euristica `h_max_pairwaise_Distance`, che combina:
       - distanza interna massima tra piante rimanenti;  
       - distanza dalla stazione se l’acqua è finita, o dalla pianta più vicina se c’è ancora acqua.

   - `a_star1()`:
     - A\* con euristica `h_manhattan`, più semplice, basata su:
       - distanza di Manhattan dalla pianta più vicina o dalla stazione,  
       - e da `finish_position` una volta irrigate tutte le piante.

7. **Visualizzazione grafica** (`visualizza_semplice`)

   - apre una finestra Matplotlib con:
     - griglia \(N \times N\) disegnata;  
     - colori distinti per rocce, stazioni, piante secche, molto secche, start, finish e robot;  
     - **trail** del percorso del robot;  
     - titolo che mostra step corrente, azione, acqua e piante rimanenti.  
   - include pulsanti:
     - **Play**: avanza automaticamente;  
     - **Pausa**: ferma l’animazione;  
     - **Indietro** / **Avanti**: navigazione manuale step-by-step.

### 3. Come eseguire `main.py`

Prerequisiti:

- `agribot_model.keras` presente nella root (ottenuto con `train.py`);  
- `test3.png` (o il tuo file immagine) posizionato nella root;  
- ambiente virtuale attivo con tutte le dipendenze installate.

Comando:

```bash
cd /percorso/AgriBot-Agent
python main.py
```

Durante l’esecuzione:

- verrà costruita e stampata la griglia in console (con colori ANSI per robot, piante, rocce, ecc.);  
- verranno lanciati in sequenza:
  - `ucs()`;  
  - `a_star()`;  
  - `a_star1()`.  
- per ogni metodo di ricerca verrà aperta una finestra Matplotlib con la **simulazione del robot**.

Se non vedi la finestra:

- verifica di non essere in un ambiente headless/solo terminale;  
- su alcune piattaforme può essere necessario usare un backend grafico compatibile o eseguire lo script da un normale ambiente desktop.

---

## Modificare parametri principali

Puoi personalizzare diversi aspetti del problema direttamente nel codice di `main.py`:

- **Dimensione della griglia**:

  ```python
  N_ROWS = 6
  N_COLS = 6
  ```

  Deve essere coerente con la griglia effettiva dell’immagine.

- **Capacità massima dell’acqua**:

  ```python
  problem = AgriBotProblem(grid_map, max_water=2)
  ```

  Aumentando `max_water` cambi il numero di irrigazioni possibili tra un rifornimento e l’altro.

- **Costi delle azioni** (nel costruttore di `AgriBotProblem`):

  ```python
  move_cost = 1
  cut_cost = 1
  water_cost = 1
  spray_cost = 3
  refill_cost = 1
  ```

  Attualmente alcuni costi (cut/spray) non sono usati, ma puoi estendere il problema per includere altre azioni (es. taglio erbacce, pesticidi).

- **Input image**:

  Come visto prima, puoi cambiare il nome del file immagine passato a `crop(...)`.

---

## Errori comuni e come risolverli

- **`ModuleNotFoundError: No module named 'tensorflow'`**  
  - Verifica di essere nell’ambiente virtuale corretto (`which python`, `python --version`);  
  - esegui `pip install tensorflow` (o la variante specifica per il tuo sistema).

- **`ModuleNotFoundError: No module named 'tensorflow_datasets'`**  
  - Installa `tensorflow-datasets`:

    ```bash
    pip install tensorflow-datasets
    ```

- **`Could not find a version that satisfies the requirement tensorflow`**  
  - Probabilmente stai usando una versione di Python non supportata.  
  - Controlla con `python --version`: deve essere **3.10.x**.  
  - Se non lo è, usa una delle strategie con `pyenv`, Conda o `python3.10` descritte in alto.

- **Il programma si chiude con messaggio “Img not found”**  
  - `grid_cell_extractor.py` non trova il file immagine;  
  - assicurati che il nome del file passato a `crop(...)` esista davvero nella root del progetto;  
  - controlla eventuali differenze tra maiuscole/minuscole o estensione `.png` / `.jpg`.

- **La finestra grafica non appare / blocco del terminale**  
  - Se stai eseguendo su un server remoto senza interfaccia grafica, Matplotlib non può aprire finestre;  
  - esegui su una macchina con desktop environment o configura un backend non interattivo (richiede modifiche al codice).

---

## Suggerimenti per l’uso e possibili estensioni

- **Testare diversi layout di campo**:  
  - crea più immagini di griglie con diverse disposizioni di D/V/R/T/S/F;  
  - confronta soluzioni e costi di UCS vs A\* con le due euristiche.

- **Raffinare il training**:
  - aumenta il numero di epoche (`epochs`) in `train.py`;  
  - modifica la struttura del modello (più layer o più filtri) per migliorare l’accuratezza;  
  - aggiungi salvataggio di metriche addizionali (confusion matrix, ecc.).

- **Nuove azioni**:
  - reintroduci e adatta azioni come `CUT` e `SPRAY` per erbacce o parassiti, gestendo nuovi insiemi nello stato (ad es. `weeds`, `pests`);  
  - assegna costi diversi a seconda del tipo di intervento.

- **Integrazione con un robot reale**:
  - il piano ottenuto (sequenza di azioni) potrebbe essere tradotto in comandi per un robot fisico (es. tramite ROS o un altro middleware), mappando UP/DOWN/LEFT/RIGHT a movimenti reali.

---

## Riepilogo rapido dei comandi principali

- **Impostare Python 3.10 con pyenv**:

  ```bash
  cd /percorso/AgriBot-Agent
  pyenv install 3.10.13        # una volta sola
  pyenv local 3.10.13
  python --version             # deve mostrare 3.10.13
  ```

- **Creare/attivare virtualenv (se non usi Conda)**:

  ```bash
  python -m venv .venv
  source .venv/bin/activate    # macOS/Linux
  # .venv\Scripts\Activate.ps1 # Windows PowerShell
  ```

- **Installare dipendenze**:

  ```bash
  pip install --upgrade pip
  pip install tensorflow tensorflow-datasets numpy matplotlib opencv-python scikit-learn
  ```

- **Addestrare il modello**:

  ```bash
  python train.py
  ```

- **Eseguire il planner e la visualizzazione**:

  ```bash
  python main.py
  ```

Seguendo queste istruzioni dovresti essere in grado di:

- configurare correttamente Python 3.10 e TensorFlow;  
- addestrare il modello di riconoscimento delle celle;  
- usare AgriBot Agent per pianificare e visualizzare il percorso ottimale del robot sul campo.

