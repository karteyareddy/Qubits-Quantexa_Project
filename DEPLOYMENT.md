# Deployment

## Local

Terminal 1:
```bash
cd backend
python -m venv .venv
# activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Terminal 2:
```bash
cd frontend
npm install
npm run dev
```

Frontend:
`http://localhost:3000`

Backend:
`http://localhost:8000`

## Environment

Backend `.env`:
```text
APP_ENV=development
CORS_ORIGINS=http://localhost:3000
RANDOM_SEED=42
SIM_TICK_SECONDS=5
OPTIMIZATION_INTERVAL_SECONDS=30
QAOA_REPS=1
QAOA_SHOTS=256
ENABLE_OSM=true
LOG_LEVEL=INFO
```

Frontend `.env.local`:
```text
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/simulation
```

Never expose secret tokens with `NEXT_PUBLIC_`.

## Docker

Use separate frontend/backend containers and docker-compose for local integrated testing.

Backend command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend command:
```bash
npm run start
```

## Production

- HTTPS
- WSS
- restricted CORS
- secrets through platform secret manager
- bounded simulation/QAOA resources
- structured logs
