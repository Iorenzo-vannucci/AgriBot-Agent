# Progetto Ristoranti

Sistema di gestione multi-ristorante con dashboard admin e menu pubblico.

## 🚀 Setup Rapido

### 1. Clona il progetto
```bash
git clone <repository-url>
cd progetto_ristoranti-main
```

### 2. Installa le dipendenze

**Backend:**
```bash
cd backend
npm install
```

**Frontend:**
```bash
cd ../frontend
npm install
```

### 3. Configurazione

Riceverai i seguenti file da configurare:
- `backend/.env` - Configurazione database e JWT
- (Altri file se necessari)

Copia i file nella cartella corretta.

### 4. Database

Il database è già configurato sul server. Se necessario, applica le migration:
```bash
cd backend
npm run migrate:deploy
```

### 5. Avvia il progetto

**Terminale 1 - Backend:**
```bash
cd backend
npm run dev
```

**Terminale 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Il backend sarà disponibile su `http://localhost:3001`  
Il frontend sarà disponibile su `http://localhost:5173`

## 📝 Note

- Il database è condiviso sul server, quindi i dati sono già presenti
- Se modifichi lo schema Prisma, esegui `npm run migrate:deploy` nel backend
- Per visualizzare il database: `cd backend && npm run prisma:studio`

## 🛠️ Comandi Utili

**Backend:**
- `npm run dev` - Avvia server sviluppo
- `npm run migrate:deploy` - Applica migration database
- `npm run prisma:studio` - Apri Prisma Studio (visualizza DB)

**Frontend:**
- `npm run dev` - Avvia dev server
- `npm run build` - Build produzione
