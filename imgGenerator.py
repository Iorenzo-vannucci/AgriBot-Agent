import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 1. Configurazione della Mappa (Copia qui la grid_map dal tuo main.py)
#    Usa lettere maiuscole standard.
grid_map = [
    ['S', '.', '.', '.', 'R', '.', '.', '.', 'D', '.', '.', '.', '.', 'R', '.', '.', '.', '.', '.', '.'],
    ['.', 'R', 'R', '.', 'R', '.', 'R', 'R', 'R', 'R', 'R', 'R', '.', 'R', '.', 'R', 'R', 'R', 'R', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'R', '.', '.', '.', '.', '.', '.', 'D', '.'],
    ['.', 'R', 'R', 'R', 'R', '.', 'R', 'R', 'R', '.', '.', 'R', 'R', 'R', 'R', 'R', '.', 'R', '.', '.'],
    ['.', 'R', 'D', '.', '.', '.', '.', '.', 'R', '.', '.', '.', '.', '.', '.', '.', '.', 'R', '.', '.'],
    ['.', 'R', '.', 'R', 'R', 'R', 'R', '.', 'R', '.', 'R', 'R', 'R', 'R', 'R', 'R', '.', 'R', 'R', '.'],
    ['.', '.', '.', 'R', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'D', 'R', '.', '.', '.', '.'],
    ['R', 'R', '.', 'R', '.', 'R', 'R', 'R', 'R', 'R', 'R', 'R', '.', 'R', '.', 'R', 'R', 'R', '.', 'R'],
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'T', '.', '.', 'R', '.', '.', '.', '.', '.', '.'],
    ['.', 'R', 'R', 'R', 'R', 'R', 'R', 'R', '.', 'R', 'R', 'R', '.', 'R', 'R', 'R', 'R', 'R', '.', '.'],
    ['.', '.', 'D', '.', '.', '.', '.', 'R', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', 'R', 'R', 'R', '.', 'R', '.', 'R', 'R', 'R', 'R', 'R', 'R', 'R', '.', 'R', 'R', 'R', 'R', '.'],
    ['.', '.', '.', '.', '.', 'R', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'R', 'D', '.', '.', '.'],
    ['.', 'R', 'R', 'R', 'R', 'R', '.', 'R', 'R', 'R', 'R', 'R', 'R', 'R', '.', 'R', '.', 'R', 'R', '.'],
    ['.', '.', '.', '.', '.', '.', '.', 'R', 'D', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
    ['R', 'R', 'R', '.', 'R', 'R', 'R', 'R', '.', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', '.', 'R'],
    ['.', 'D', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', '.', 'R', 'R', 'R', 'R', 'R', 'R', 'R', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'D', '.', '.', '.', '.', '.'],
    ['.', 'R', '.', '.', '.', '.', '.', 'R', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'F']
]

def create_grid_image(grid, filename="agribot_map_L1.png"):
    rows = len(grid)
    cols = len(grid[0])
    
    # Crea una figura
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Disegna la griglia e le lettere
    for i in range(rows):
        for j in range(cols):
            cell_val = grid[i][j]
            
            # Coordinate per disegnare (Matplotlib ha origine in basso a sinistra, invertiamo y)
            x = j
            y = rows - 1 - i
            
            # Colore di sfondo opzionale per leggibilità (bianco per tutti)
            rect = patches.Rectangle((x, y), 1, 1, linewidth=1, edgecolor='black', facecolor='white')
            ax.add_patch(rect)
            
            # Se la cella non è vuota ('.'), scriviamo la lettera
            if cell_val != '.':
                # Mappiamo le lettere del tuo codice su quelle richieste dal PDF se serve
                # Tuo codice: R (Rock), PDF: X (Inaccessibile) -> Qui stampiamo quello che vuoi RILEVARE
                # Per coerenza col tuo main.py stampiamo le TUE lettere: S, F, R, D, T
                
                font_weight = 'bold'
                color = 'black'
                
                
                ax.text(x + 0.5, y + 0.5, cell_val, 
                        horizontalalignment='center', 
                        verticalalignment='center', 
                        fontsize=20, 
                        color=color,
                        fontweight=font_weight)

    # Impostazioni finali grafico
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.axis('off') # Nasconde gli assi numerici
    
    # Salva immagine senza bordi bianchi extra
    plt.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=100)
    plt.close()
    print(f"✅ Immagine generata con successo: {filename}")

if __name__ == "__main__":
    create_grid_image(grid_map)