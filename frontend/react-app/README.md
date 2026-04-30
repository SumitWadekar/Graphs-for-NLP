React frontend for Contract Analysis

Quick start:

1. Install dependencies

```bash
cd frontend/react-app
npm install
```

2. Run dev server

```bash
npm run dev
```

The dev server runs on port 5173 by default. The frontend assumes the backend is reachable at the same host (relative paths like `/upload-contract-csv`). If backend runs on a different port (e.g., 8000), use a dev proxy in `vite.config.js` or run the frontend with a CORS-enabled backend.
