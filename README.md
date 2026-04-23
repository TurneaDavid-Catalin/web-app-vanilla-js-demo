## Web App (Vanilla JS) Demo

Single-page web app built with **Vanilla JavaScript** that showcases core **Web Platform APIs** (e.g. **IndexedDB**, **Web Worker**) and a minimal **custom Python HTTP server**.

### Highlights
- **SPA navigation**: dynamic content loading from `index.html` (no framework).
- **User register & login**: register via `POST /api/utilizatori`, login by validating against stored users.
- **IndexedDB**: persistent client-side storage for app data.
- **Web Worker**: background processing without blocking the UI.
- **XML rendering**: renders a table from `resurse/persoane.xml`.

### Tech stack
- **Frontend**: HTML, CSS, Vanilla JS
- **Backend**: minimal Python socket-based HTTP server
- **Data**: JSON (`resurse/utilizatori.json`), XML (`resurse/persoane.xml`)

### Run locally (Windows)
1. Start the server:

```bash
python server_web/server_web.py
```

2. Open the app in the browser:
- Go to `http://localhost:5678/`

> Note: features that load resources via HTTP (e.g. `persoane.xml`, `utilizatori.json`) may not work correctly if you open files directly via `file://`. Use the local server.

### Project structure
- `continut/` – frontend (HTML/CSS/JS) + static resources
  - `index.html` – entry point + SPA loader
  - `js/` – client scripts (including `worker.js`)
  - `resurse/` – app data (XML/JSON/DTD)
- `server_web/` – Python HTTP server (`server_web.py`)

### Notes
- Passwords are stored **in plain text** in `utilizatori.json` (demo/educational scope).
- This repository is intended as a **learning/demo project** showcasing web fundamentals.
