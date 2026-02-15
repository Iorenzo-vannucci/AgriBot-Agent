import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import tensorflow as tf
from grid_cell_extractor import crop

# --- Parametri ---
N_ROWS = 6
N_COLS = 6
LABELS = ['D', 'F', 'R', 'S', 'T', '.', 'V']

# --- Carica modello e ritaglia celle ---
model = tf.keras.models.load_model("agribot_model.keras")
cells = crop("test3.png", N_ROWS, N_COLS)

# --- Classifica ogni cella ---
grid_map = []
row = []
predictions = []
for i, j, cell_img in cells:
    normalized = cell_img.astype("float32") / 255.0
    normalized = normalized.reshape(1, 28, 28, 1)
    pred = model.predict(normalized, verbose=0)
    idx = np.argmax(pred)
    conf = pred[0][idx] * 100
    char = LABELS[idx]
    predictions.append((i, j, cell_img, char, conf))
    row.append(char)
    if j == N_COLS - 1:
        grid_map.append(row)
        row = []

# --- FIGURA ---
fig = plt.figure(figsize=(18, 10))
gs = gridspec.GridSpec(1, 2, width_ratios=[3, 2], wspace=0.3)

# === PANNELLO SINISTRO: griglia celle 28×28 con predizione ===
gs_left = gridspec.GridSpecFromSubplotSpec(N_ROWS, N_COLS, subplot_spec=gs[0], hspace=0.4, wspace=0.2)

for i, j, cell_img, char, conf in predictions:
    ax = fig.add_subplot(gs_left[i, j])
    ax.imshow(cell_img, cmap="gray")
    color = "lime" if char != '.' else "white"
    ax.set_title(f"{char}\n{conf:.0f}%", fontsize=10, fontweight="bold", color=color)
    ax.axis("off")

# === PANNELLO DESTRO: mappa logica come tabella ===
ax_table = fig.add_subplot(gs[1])
ax_table.axis("off")
ax_table.set_title("Mappa Logica (grid_map)", fontsize=14, fontweight="bold", pad=20)

# Colori per ogni tipo di cella
cell_colors = {
    'S': '#E8A0E8',  # magenta chiaro
    'F': '#FFD700',  # oro
    'R': '#B0B0B0',  # grigio
    'D': '#FFA500',  # arancione
    'V': '#FF6B6B',  # rosso chiaro
    'T': '#87CEEB',  # azzurro
    '.': '#FFFFFF',  # bianco
}

table_data = grid_map
colors = [[cell_colors.get(c, '#FFFFFF') for c in row] for row in grid_map]

table = ax_table.table(
    cellText=table_data,
    cellColours=colors,
    cellLoc='center',
    loc='center',
    bbox=[0.1, 0.05, 0.8, 0.85]
)
table.auto_set_font_size(False)
table.set_fontsize(16)
for key, cell in table.get_celld().items():
    cell.set_edgecolor('black')
    cell.set_linewidth(1.5)
    cell.set_height(0.14)

# Legenda sotto la tabella
legend_items = [('S', 'Start'), ('F', 'Finish'), ('R', 'Roccia'),
                ('D', 'Pianta secca'), ('V', 'Molto secca'), ('T', 'Stazione'), ('.', 'Vuota')]
legend_str = "   ".join([f"{sym} = {desc}" for sym, desc in legend_items])
ax_table.text(0.5, -0.02, legend_str, ha='center', va='top', fontsize=9,
              transform=ax_table.transAxes, color='gray')

plt.suptitle("Classificazione CNN → Mappa Logica", fontsize=16, fontweight="bold")
plt.savefig("cnn_mappa_logica.png", dpi=150, bbox_inches="tight")
plt.show()