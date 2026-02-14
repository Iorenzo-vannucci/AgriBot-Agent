# 🤖 AgriBot-Agent: Autonomous Agricultural Robot
**Progetto di Introduzione all'Intelligenza Artificiale**

AgriBot è un agente intelligente progettato per operare in un ambiente agricolo simulato. Il suo obiettivo è analizzare visivamente una mappa del campo, identificare piante che necessitano di acqua, e pianificare il percorso ottimale per innaffiarle tutte gestendo risorse limitate (acqua ed energia).

---

## 📋 Indice
1. [Descrizione del Problema](#descrizione-del-problema)
2. [Architettura del Sistema](#architettura-del-sistema)
3. [Tecnologie Utilizzate](#tecnologie-utilizzate)
4. [Dettagli Implementativi](#dettagli-implementativi)
   - [Visione (Cropping & OCR)](#1-visione-cropping--ocr)
   - [Modellazione (Stati e Azioni)](#2-modellazione-stati-e-azioni)
   - [Pianificazione (A* ed Euristiche)](#3-pianificazione-a-ed-euristiche)
5. [Installazione ed Esecuzione](#installazione-ed-esecuzione)
6. [Risultati e Statistiche](#risultati-e-statistiche)

---

## 🌍 Descrizione del Problema

L'ambiente è rappresentato da una griglia $N \times N$ dove ogni cella può contenere:
- **S (Start)**: Posizione iniziale del robot.
- **F (Finish)**: Posizione finale da raggiungere.
- **R (Rock)**: Ostacolo invalicabile.
- **D (Dry Plant)**: Pianta secca (richiede 1 unità d'acqua).
- **V (Very Dry Plant)**: Pianta molto secca (richiede 2 unità d'acqua).
- **T (Tank)**: Stazione di rifornimento acqua.
- **. (Empty)**: Terreno percorribile.

**Vincoli:**
- Il robot ha un serbatoio con capacità limitata (`max_water`).
- Il movimento ha costo 1.
- Innaffiare ha costo 1 e consuma acqua.
- Ricaricare (Refill) ha costo 1 e riempie il serbatoio.
- L'obiettivo è innaffiare **tutte** le piante (D e V) e raggiungere F.

---

## 🏗 Architettura del Sistema

Il progetto è strutturato in una pipeline sequenziale:

```mermaid
graph LR
    A[Immagine Input] --> B[Cropping (CV2)]
    B --> C[Classificazione (CNN)]
    C --> D[Mappa Logica]
    D --> E[Pathfinding (A*)]
    E --> F[Simulazione Azioni]
```

### File Principali
- **`cropping.py`**: Modulo di Computer Vision. Rileva la griglia nell'immagine, corregge la prospettiva e ritaglia le singole celle.
- **`train.py`**: Script per l'addestramento della Rete Neurale (CNN) sul dataset EMNIST Balanced (esteso con classi custom).
- **`main.py`**: Core del sistema. Integra visione, definizione del problema (metodo `AgriBotProblem`) e algoritmi di ricerca.
- **`agribot_model.keras`**: Modello pre-addestrato per il riconoscimento dei caratteri.

---

## 🛠 Tecnologie Utilizzate

- **Python 3.12**: Linguaggio principale.
- **OpenCV (`cv2`)**: Per elaborazione immagini (thresholding, contour detection, perspective warp).
- **TensorFlow / Keras**: Per la costruzione e training della Convolutional Neural Network (CNN).
- **AIMA-Python**: Libreria base per gli algoritmi di ricerca nello spazio degli stati (A*, UCS).
- **Matplotlib**: Per la visualizzazione dei grafici di training e della simulazione finale.
- **NumPy**: Per manipolazione matrici e dati.

---

## 🔍 Dettagli Implementativi

### 1. Visione: Cropping & OCR
Il modulo `cropping.py` deve gestire immagini reali (disegnate a mano o stampate).
- **Griglia**: Utilizza un algoritmo basato sulla somma dei pixel (proiezione su assi X/Y) e `find_peaks` per individuare le linee della griglia anche se disegnate col pennarello (grazie a parametri ottimizzati come `sigma` ridotto per linee spesse).
- **OCR**: Una CNN addestrata riconosce 7 classi: `['D', 'F', 'R', 'S', 'T', '.', 'V']`.
  - Abbiamo aggiunto la classe **V (Very Dry)** mappandola ad un carattere EMNIST specifico.
  - Abbiamo introdotto "celle vuote nere" nel training set per evitare falsi positivi.

### 2. Modellazione: Stati e Azioni
Lo stato del robot è definito dalla tupla:  
`(posizione, acqua_corrente, set_piante_D, set_piante_V)`

Le azioni possibili (`UP`, `DOWN`, `LEFT`, `RIGHT`, `WATER`, `REFILL`) sono generate dinamicamente solo se valide (es. non posso fare `WATER` se non ho acqua o non sono su una pianta).

### 3. Pianificazione: A* ed Euristiche
Abbiamo confrontato **Uniform Cost Search (UCS)** (cieco) con **A*** (informato).
Per A*, abbiamo sviluppato due euristiche:

1. **`h_manhattan`**: 
   - Calcola la distanza Manhattan verso l'obiettivo più vicino (pianta se ho acqua, stazione se sono scarico, o fine se ho finito).
   - *Vantaggio*: Veloce. *Svantaggio*: Sottostima troppo in casi complessi.

2. **`h_max_pairwise_Distance` (Euristica Avanzata)**:
   - Oltre alla distanza verso l'obiettivo più vicino, aggiunge la **massima distanza interna** tra le piante rimaste (diametro del set di obiettivi).
   - *Risultato*: Molto più efficiente, riduce drasticamente i nodi espansi evitando di "vagare" inutilmente.

---

## 🚀 Installazione ed Esecuzione

### Prerequisiti
```bash
pip install numpy opencv-python matplotlib scipy tensorflow tensorflow-datasets scikit-learn
```

### Esecuzione
1. **Training (opzionale se hai già il modello):**
   ```bash
   python train.py
   # Genera agribot_model.keras
   ```

2. **Test Cropping (opzionale):**
   ```bash
   python cropping.py
   # Verifica se l'immagine viene ritagliata correttamente
   ```

3. **Avvio Agente:**
   ```bash
   python main.py
   # Esegue la pipeline completa e mostra la simulazione grafica
   ```

---

## 📊 Risultati e Statistiche

Esempio di esecuzione su mappa 6x6 complessa:

| Algoritmo | Euristica | Nodi Esplorati | Costo Soluzione | Tempo |
|-----------|-----------|----------------|-----------------|-------|
| **UCS** | Nessuna | ~6800 | 27 | Lento |
| **A\*** | Manhattan | ~6200 | 27 | Medio |
| **A\*** | **Max Pairwise** | **~5700** | **27** | **Ottimo** |

L'euristica `Max Pairwise` si è dimostrata la più efficiente, riducendo lo spazio di ricerca di circa il **15-20%** rispetto a UCS, garantendo comunque l'ottimalità della soluzione.

---
**Autore:** Tommaso Lauria