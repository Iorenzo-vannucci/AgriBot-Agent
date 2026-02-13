import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input
from tensorflow.keras.layers import RandomRotation, RandomZoom
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
import cv2
import matplotlib.pyplot as plt 

# --- CONFIGURAZIONE ---
IMG_SIZE = 28
# Mappatura EMNIST: 13=D, 15=F, 27=R, 28=S, 29=T
TARGET_MAP = {13: 0, 15: 1, 27: 2, 28: 3, 29: 4} 
CLASSES = ['D', 'F', 'R', 'S', 'T', '.'] 

def load_data_tfds():
    print(" Scarico EMNIST Balanced via TensorFlow Datasets...")
    ds = tfds.load('emnist/balanced', split='train', as_supervised=True, shuffle_files=True)
    
    x_data = []
    y_data = []

    print("Filtro ed estraggo i dati...")
    for image, label in tfds.as_numpy(ds):
        lbl = int(label)
        if lbl in TARGET_MAP:
            img = image.reshape(28, 28)
            img = np.transpose(img)
            x_data.append(img)
            y_data.append(TARGET_MAP[lbl])

    X = np.array(x_data)
    Y = np.array(y_data)

    print("Background: Genero celle vuote (rumore)...")
    n_noise = len(X) // 5
    x_noise = []
    
    for _ in range(n_noise):
        img = np.zeros((28, 28), dtype=np.uint8)
        noise = np.random.randint(0, 50, (28, 28), dtype=np.uint8)
        img = cv2.add(img, noise)
        x_noise.append(img)
    
    X = np.concatenate((X, np.array(x_noise)), axis=0)
    Y_noise = np.full(len(x_noise), 5)
    Y = np.concatenate((Y, Y_noise), axis=0)

    X = X.reshape(-1, IMG_SIZE, IMG_SIZE, 1).astype('float32') / 255.0
    Y = to_categorical(Y, num_classes=6)
    
    print(f"Dataset caricato: {len(X)} immagini pronte.")
    return X, Y

def build_model():
    model = Sequential([
        Input(shape=(IMG_SIZE, IMG_SIZE, 1)),
        RandomRotation(0.1), 
        RandomZoom(0.1),

        Conv2D(32, (3, 3), activation='relu', padding='same'),
        MaxPooling2D((2, 2)),
        Dropout(0.2),

        Conv2D(64, (3, 3), activation='relu', padding='same'),
        MaxPooling2D((2, 2)),
        Dropout(0.2),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.4),
        Dense(6, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def plot_history(history):
    """Genera e salva i grafici delle prestazioni"""
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs = range(1, len(acc) + 1)

    # 1. Grafico Precisione (Accuracy)
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epochs, acc, 'bo-', label='Training Accuracy')
    plt.plot(epochs, val_acc, 'ro-', label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoche')
    plt.ylabel('Precisione')
    plt.legend()

    # 2. Grafico Errore (Loss)
    plt.subplot(1, 2, 2)
    plt.plot(epochs, loss, 'bo-', label='Training Loss')
    plt.plot(epochs, val_loss, 'ro-', label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoche')
    plt.ylabel('Errore')
    plt.legend()

    plt.savefig('statistiche_training.png')
    print("\n Grafico salvato come 'statistiche_training.png'")
    plt.show()

def main():
    X, Y = load_data_tfds()
    X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.2, stratify=Y)
    
    model = build_model()
    
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    print("🏋️  Inizio training...")
    # Salviamo la storia dell'allenamento nella variabile 'history'
    history = model.fit(X_train, Y_train, 
              validation_data=(X_val, Y_val),
              epochs=30, 
              batch_size=64, 
              callbacks=[early_stop])
    
    model.save("agribot_model.keras")
    print(" Modello salvato: agribot_model.keras")

    # --- GENERAZIONE GRAFICI ---
    plot_history(history)

if __name__ == "__main__":
    main()