import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.signal import find_peaks, peak_widths
from scipy.ndimage import gaussian_filter1d
import sys

DIM = 1000  # dimensione warp
def crop(filename, n_rows, n_cols):
    # Carica e trova la griglia
    img = cv2.imread(filename)
    if img is None: 
        print("Img not found")
        sys.exit()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #conversione da scala di colori a scala di grigi 
    _, negative_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU) #otsu calcola automaticamente la soglia di colori ottimale

    find_contours , _= cv2.findContours(negative_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #retr external considera solo il perimetro esterno escludendo la parte interna, chainApprox che comprime segmenti lineari, prende solo gli estremi di una linea 
    find_biggest_contours  = sorted(find_contours, key=cv2.contourArea, reverse=True) #la funzione sorted ordina in ordine decrescente i valori trovati (reverse = True)

    if not find_biggest_contours: 
        print("Grid not found")
        sys.exit()

    def order_points(corners):
        TL_BR = corners.sum(1) #Top Left e Bottom Right; somma x e y per ogni angolo
        TR_BL = (corners[:,0] - corners[:,1]) #è come se facessi x - y iterando i signoli valori
        src = np.float32([corners[np.argmin(TL_BR)], corners[np.argmax(TR_BL)], corners[np.argmax(TL_BR)], corners[np.argmin(TR_BL)]])
        return src

    corners = None

    c = find_biggest_contours[0] #prendo contorno più grande
    corners = cv2.boxPoints(cv2.minAreaRect(c)).astype(np.float32) #BoxPoints serve a raddrizzare la griglia prima di tagliare le celle, restituisce 4 angoli partendo dal centro la dimensione e l'angolo restituiti da minAreaReact; minAreaReact usa un rettangolo ruotato, per aderire perfettamente al bordo dell'input passato
    src = order_points(corners)
    dst = np.float32([[0,0],[DIM-1,0],[DIM-1,DIM-1],[0,DIM-1]])
    warped = cv2.warpPerspective(gray, cv2.getPerspectiveTransform(src, dst), (DIM, DIM))
    warped = cv2.morphologyEx(
    cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1],
        cv2.MORPH_OPEN, np.ones((3,3), np.uint8))


    # 2. Trova intervalli celle 
    def get_intervals(proj, n):
        # Filtro più deciso per unificare le righe del pennarello
        p = gaussian_filter1d(proj, sigma=5)
        
        # Distanza minima forzata: le righe non possono essere più vicine di metà della cella ideale
        expected_size = DIM / n
        min_distance = int(expected_size * 0.5)
        
        # Cerca picchi. Prominence adattiva.
        peaks, _ = find_peaks(p, prominence=p.max()*0.2, distance=min_distance) 
        
        # Se non trovo abbastanza righe, fallback matematico standard
        if len(peaks) < n-1:
            return [(int(i*DIM/n), int((i+1)*DIM/n)) for i in range(n)]

        # COSTRUZIONE MURI
        #diminusici questo valore in base allo spessore della linea #per immagine 
        #img4 ho usato 32
        #test3 ho usato 10

        WALL_HALF_WIDTH = 10

        walls = []
        for pk in peaks:
            walls.append(max(0, int(pk - WALL_HALF_WIDTH))) # Inizio muro
            walls.append(min(DIM, int(pk + WALL_HALF_WIDTH))) # Fine muro
        
        bounds = [0] + walls + [DIM]
        gaps = [(bounds[i]+4, bounds[i+1]-4) for i in range(0, len(bounds)-1, 2)]
        
        valid_gaps = []
        for gap in gaps:
            width = gap[1] - gap[0]
            if width >10: # Scarta cose troppo piccole per essere celle
                valid_gaps.append(gap)
                
        # SELEZIONE GAP MIGLIORE:
        # Invece di prendere i più grandi (rischio di unire due celle),
        # prendiamo quelli più vicini alla dimensione ideale (expected_size).
        valid_gaps.sort(key=lambda x: abs((x[1]-x[0]) - expected_size))
        
        # Prendi i migliori 'n', poi riordinali per posizione (sinistra->destra)
        return sorted(valid_gaps[:n], key=lambda x: x[0])

    # Richiamo (fondamentale passare la proiezione corretta)
    rows = get_intervals(warped.sum(axis=1), n_rows)
    cols = get_intervals(warped.sum(axis=0), n_cols)

    # --- 3. Pulisci ogni cella ---
    def clean_cell(cell):
        cell[:3,:] = cell[-3:,:] = cell[:,:3] = cell[:,-3:] = 0 #creo un bordo nero di 3px per eliminare residui delle linee della griglia
        n, labels, stats, _ = cv2.connectedComponentsWithStats(cell) #analizza immagine e raggruppa pixel bianchi che si trovano vicini tra loro
        if n < 2: 
            return np.zeros((28,28), np.uint8) #se l'isola è troppo piccola mettiamo direttamente lo sfondo nero
        best_idx = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])   #con stats prendo le informazioni sulle "isole" (pixel) a partire dall'isola 1 
                                                                #(0 sarebbe l'area più grande ovvero lo sfondo nero). cv2CC_STAT dice di considerare tutto
                                                                #il blocco di pixel uniti (area) che verrà preso da argmax. Aggiungo 1 per la colonna 
                                                                #aggiunta intorno. Returna l'indice dell'isola maggiore trovata

        x, y, w, h, area = stats[best_idx]  #x,y coordinate ancgolo in alto a sinistra del rettangolo che contene l'oggetto
                                            #w larghezza del rettangolo, h altezza del rettangolo
        
        # Filtro proporzionale: l'oggetto deve occupare almeno il 2% dell'area della cella.
        # Una lettera reale occupa tipicamente il 5-20%, mentre un artefatto/residuo di
        # linea occupa meno dell'1-2%. Questo filtro è robusto per qualsiasi dimensione di griglia.
        H_cell, W_cell = cell.shape
        cell_area = H_cell * W_cell
        if area < cell_area * 0.02: #se l'oggetto occupa meno del 2% della cella, è rumore
            return np.zeros((28, 28), np.uint8)
        
        rapporto = w / h
        if rapporto > 5 or rapporto < 0.2: #se l'area è molto sproporzionata in lunghezza o larghezza setto a nero
            return np.zeros((28, 28), np.uint8)
        
        is_vertical_line = w < 6 and (h > H_cell * 0.5) #se l'oggetto è molto fino ma anche lungo allora fa parte della griglia verticale
        is_horizontal_line = h < 6 and (w > W_cell * 0.5) #se l'oggetto è molto fino ma anche largo allora fa parte della linea orizzonatale
        if is_vertical_line or is_horizontal_line:
            return np.zeros((28, 28), np.uint8)
        digit = (labels[y:y+h, x:x+w] == best_idx).astype(np.uint8) * 255   #ritaglio dalla mapp solo il rettangolo in cui si trova la lettera (ottengo una nuova mappa con TRUE e FALSE)
                                                                            #faccio casting a 0,1 e moltiplico per 255 per avere il bianco
        
        # Calcola quanto bordo nero aggiungere sopra/sotto e destra/sinistra
        bordo = max(w, h) + 6 #il qudrato deve essere lungo almeno quanto il lato più lungo della lettera, 6 è quello che aggiungo per dare spazio
        dy, dx = (bordo - h), (bordo - w)
        
        # Aggiungi i bordi: ((Top, Bottom), (Left, Right))
        square = np.pad(digit, ((dy//2, dy - dy//2), (dx//2, dx - dx//2)))  # np.pad va a riempire sopra sotto, destra/sinistra di pixel neri fino a raggiungere lo spazio desiderato
                                                                            # questo lo rappresento con una tupla di tuple ((sopra, sotto), (sinistra, destra))

        return cv2.resize(square, (28, 28), interpolation=cv2.INTER_AREA) #interpolation è un metodo matematico per evitare di avere linee troppo pixelose quando vado a ridimensionare l'immagine

    # --- 4. Estrai tutte le celle ---
    cells = []
    for i, r in enumerate(rows[:n_rows]):
        for j, c in enumerate(cols[:n_cols]):
            cells.append((i, j, clean_cell(warped[r[0]:r[1], c[0]:c[1]])))  #dove i è il numero della riga, j della colonna r[0]:R[1] dimensione della cella rispetto alla riga relativamente la stessa cosa per c 
    #print(cells[0])
    return cells

if __name__ == "__main__":
    n_rows = 5
    n_cols = 5
    cells = crop("img4.png", n_rows, n_cols )
    # --- 5. Visualizza griglia ---
    fig1, axes = plt.subplots(n_rows, n_cols , figsize=(8, 8))
    for i, j, cell in cells:
        axes[i, j].imshow(cell, cmap="gray")
        axes[i, j].axis("off")
    plt.tight_layout()

    # --- 6. Visualizza cella singola con slider ---
    fig2, ax2 = plt.subplots(figsize=(4, 4))
    plt.subplots_adjust(bottom=0.2)
    im = ax2.imshow(cells[0][2], cmap="gray")
    ax2.axis("off")
    title = ax2.set_title(f"Cella (0, 0) — 1/{len(cells)}")

    slider_ax = fig2.add_axes([0.15, 0.06, 0.7, 0.04])
    slider = Slider(slider_ax, "Cella", 0, len(cells)-1, valinit=0, valstep=1)

    def update(val):
        idx = int(slider.val)
        i, j, cell = cells[idx]
        im.set_data(cell)
        ax2.set_title(f"Cella ({i}, {j}) — {idx+1}/{len(cells)}")
        fig2.canvas.draw_idle()

    slider.on_changed(update)

    def on_key(event):
        if event.key == "right" and slider.val < len(cells)-1:
            slider.set_val(slider.val + 1)
        elif event.key == "left" and slider.val > 0:
            slider.set_val(slider.val - 1)

    fig2.canvas.mpl_connect("key_press_event", on_key)

    plt.show()