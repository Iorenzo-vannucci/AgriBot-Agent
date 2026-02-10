import cv2
import numpy as np
import os
import matplotlib.pyplot as plt


N_ROWS = 20
N_COLS = 20 
FILENAME = "agribot_map_L1.png" 

def visualize_grid_matplotlib(all_cells, coords):
    """
    Visualizza le celle usando Matplotlib con navigazione tramite 
    Frecce e Rotella del Mouse.
    """
    total = len(all_cells)
    current_idx = 0 # Indice della cella corrente

    # Creiamo la figura e gli assi
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Funzione interna per aggiornare l'immagine
    def update_image():
            ax.clear()
            ax.axis('off')
            ax.imshow(all_cells[current_idx], cmap='gray')
            fig.canvas.draw()

    # --- GESTORE TASTIERA (Frecce e Q) ---
    def on_key(event):
        nonlocal current_idx # Permette di modificare la variabile esterna
        
        if event.key == 'right': # Freccia destra: Avanti
            if current_idx < total - 1:
                current_idx += 1
                update_image()
        elif event.key == 'left': # Freccia sinistra: Indietro
            if current_idx > 0:
                current_idx -= 1
                update_image()
        elif event.key == 'q': # Q: Esci
            plt.close(fig)

    # --- GESTORE MOUSE (Rotella) ---
    def on_scroll(event):
        nonlocal current_idx
        
        # event.button può essere 'up' (su) o 'down' (giù)
        if event.button == 'up': # Scrollo su -> Indietro 
            if current_idx > 0:
                current_idx -= 1
                update_image()
        elif event.button == 'down': # Scrollo giù -> Avanti
            if current_idx < total - 1:
                current_idx += 1
                update_image()

    # Colleghiamo gli eventi alla figura
    fig.canvas.mpl_connect('key_press_event', on_key)
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    # Mostriamo la prima immagine
    update_image()
    plt.show()

def find_countours(img):
    #dobbiamo trasformare tutto ciò che non è puro bianco in nero e invertire i colori
    #con la funzione threshold riesco a separare un oggetto dalla sfondo usa una soglia, per i valori che la superano gli assegnamo 255 
    #il primo valore di ritorno della funzione threshold è il valore numerico della soglia che a noi non interessa quindi _ 

    #_, img_bin = cv2.threshold(img,200 , 255, cv2.THRESH_BINARY_INV) #THRESH_BINARY_INV si usa quando ho qualcosa su sfondo chiaro 
    img_bin = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2) #evoluzionerispetto al normale threshold, in questo modo anche con sfumature di un foglio di carta dovrebbe andare
    contours, _ = cv2.findContours(img_bin,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #ritorna una lista Python di array NumPy. Ogni array contiene le coordinate (x,y) dei punti che formano il perimetro.
    #cerco nella lista dei contorni quello con l'area più grnade
    max_area=0
    best_rect= (0,0, img.shape[1], img.shape[0]) #immagine intera di

    for i in contours:
        area = cv2.contourArea(i)
        #print(area)
        if area > 5000: 
            if area > max_area:
                max_area = area
                x, y, w, h = cv2.boundingRect(i)
                best_rect = (x, y, w, h)

    x, y, w, h = best_rect
    # Restituisce l'immagine ritagliata esattamente sui bordi della griglia
    cropped_img = img [y:y+h, x:x+w]
    #print(cropped_img)
    return cropped_img

def slide_grid():
    img = cv2.imread(FILENAME,0) #lo zero è un flag per caricare l'immagine in scala di grigi. 
    if img is None: 
        print("il path non è correto")
        return
    
    img = find_countours(img)

    #preleviamo le dimensioni dell'immagine con shape
    h_img,w_img= img.shape
    
    y_steps = np.linspace(0, h_img, N_ROWS + 1).astype(int)
    x_steps = np.linspace(0, w_img, N_COLS + 1).astype(int)
    all_cells = []
    coords = []
    for r in range(N_ROWS):
        for c in range(N_COLS):
            # Prendo le coordinate dai vettori calcolati
            y_start = y_steps[r]
            y_finish = y_steps[r+1]
            x_start = x_steps[c]
            x_finish = x_steps[c+1]

            # Opzionale: Se vuoi forzare più bordo, puoi allargare leggermente la selezione
            # stando attento a non uscire dall'immagine (clamp)
            margin = 3
            cropped_cell = img[max(0, y_start+margin):min(h_img, y_finish-margin), 
                               max(0, x_start+margin):min(w_img, x_finish-margin)]
            
            #cropped_cell = img[y_start:y_finish, x_start:x_finish]
            all_cells.append(cropped_cell)
            coords.append((r,c))
    
    """
    #visulizzazione ingrandita delle celle separate
    count=0
    total = len(all_cells)
    while True:
        current_cell = all_cells[count]
        r,c = coords[count]
        #zoom della cella per vederla bene utilizzando la funzione resize della libreria OpenCV
        zoomed_cell= cv2.resize(current_cell,(250,250),interpolation = cv2.INTER_CUBIC) #interpolation serve per specificare l'algo utilizzato per aggiungere o rim pixel ho scelto CUBIC perchè veloce e qualità ottima
        window_coords = f"Row: {r} Col: {c}"
        cv2.imshow(window_coords,zoomed_cell)
        key = cv2.waitKey(0)
        # Gestione Tasti
        if key == ord('q') or key == 27: # Q o ESC
            break
        elif key == ord(' ') or key == ord('d'): # SPAZIO o D (Avanti)
            if count < total - 1:
                count += 1
        elif key == ord('a'): # A (Indietro)
            if count > 0:
                count -= 1
        
        cv2.destroyAllWindows()
    """

    visualize_grid_matplotlib(all_cells, coords)

if __name__ == "__main__":
    slide_grid()